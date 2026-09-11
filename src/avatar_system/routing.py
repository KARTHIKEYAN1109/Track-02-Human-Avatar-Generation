"""
Execution routing and engine dispatch module for the Human Avatar System.
Supports Kaggle accelerator workflow, local hardware execution, and deterministic mock runners for CI/testing.
"""

from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

from avatar_system.config import SystemConfig, default_config
from avatar_system.exceptions import JobExecutionError
from avatar_system.provenance import ProvenanceManager, compute_file_sha256
from avatar_system.schemas import JobBundle, ProvenanceManifest


class MockInferenceEngine:
    """
    Deterministic mock generator for offline CPU testing, CI environments, and validation.
    Generates a valid, decodable PNG image with color coding derived from the spec attributes
    and deterministic seed.
    """

    @staticmethod
    def generate(job_bundle: JobBundle, output_image_path: Path) -> Dict[str, Any]:
        start_time = time.time()
        width = job_bundle.metadata.width
        height = job_bundle.metadata.height

        # Derive background color from background attribute
        bg_colors = {
            "neutral_studio": (220, 224, 230),
            "neutral_studio_grey": (200, 204, 208),
            "minimalist_modern_office": (235, 240, 245),
            "sunlit_library": (245, 235, 215),
            "architectural_concrete": (180, 185, 190),
            "soft_warm_gradient": (250, 230, 210),
        }
        bg = bg_colors.get(job_bundle.avatar_spec.background, (225, 225, 230))

        # Skin tone color palette
        skin_colors = {
            "fair": (255, 224, 189),
            "light_olive": (230, 200, 160),
            "medium_warm": (210, 165, 120),
            "rich_bronze": (160, 105, 60),
            "deep_ebony": (90, 55, 35),
            "warm_tan": (220, 175, 130),
        }
        skin = skin_colors.get(job_bundle.avatar_spec.skin_tone, (215, 175, 135))

        # Hair color palette
        hair_colors = {
            "black": (30, 30, 30),
            "dark_brown": (65, 45, 30),
            "golden_blonde": (230, 195, 95),
            "auburn": (150, 60, 35),
            "silver_grey": (185, 190, 195),
        }
        hair = hair_colors.get(job_bundle.avatar_spec.hair, (50, 40, 35))

        # Attire color
        attire_color = (60, 80, 110)

        # Create PIL Image
        img = Image.new("RGB", (width, height), color=bg)
        draw = ImageDraw.Draw(img)

        center_x = width // 2
        center_y = height // 2

        # Draw torso / attire
        torso_box = [center_x - width // 3, center_y + height // 6, center_x + width // 3, height]
        draw.ellipse(torso_box, fill=attire_color)

        # Draw head / face
        head_radius = min(width, height) // 4
        head_box = [center_x - head_radius, center_y - head_radius - 20, center_x + head_radius, center_y + head_radius - 20]
        draw.ellipse(head_box, fill=skin)

        # Draw hair cap
        hair_box = [center_x - head_radius - 4, center_y - head_radius - 28, center_x + head_radius + 4, center_y - 10]
        draw.chord(hair_box, start=180, end=360, fill=hair)

        # Draw eyes
        eye_y = center_y - 25
        eye_spacing = head_radius // 2
        draw.ellipse([center_x - eye_spacing - 6, eye_y - 4, center_x - eye_spacing + 6, eye_y + 4], fill=(40, 40, 40))
        draw.ellipse([center_x + eye_spacing - 6, eye_y - 4, center_x + eye_spacing + 6, eye_y + 4], fill=(40, 40, 40))

        # Watermark label: Synthetic Media
        draw.rectangle([0, height - 24, width, height], fill=(20, 20, 20, 200))
        draw.text((10, height - 18), f"AI-GENERATED SYNTHETIC AVATAR | SEED: {job_bundle.seed}", fill=(240, 240, 240))

        output_image_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_image_path, format="PNG")
        duration = time.time() - start_time

        return {
            "engine": "mock_inference_engine",
            "duration_sec": round(duration, 4),
            "device": "cpu_synthetic",
            "vram_peak_mb": 0.0,
            "system_ram_mb": 45.0,
        }


class ExecutionRouter:
    """Routes job execution to the appropriate backend."""

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or default_config

    def execute_job(
        self,
        job_bundle: JobBundle,
        route: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ) -> ProvenanceManifest:
        """
        Dispatches execution based on the requested route.
        """
        target_dir = output_dir or self.config.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        chosen_route = route or job_bundle.metadata.route
        img_filename = f"{job_bundle.avatar_spec.avatar_id}_{job_bundle.seed}.png"
        img_path = target_dir / img_filename
        manifest_path = target_dir / f"{job_bundle.avatar_spec.avatar_id}_{job_bundle.seed}_manifest.json"

        if chosen_route == "mock_runner":
            telemetry = MockInferenceEngine.generate(job_bundle, img_path)
            manifest = ProvenanceManager.create_manifest(
                job_bundle=job_bundle,
                status="success",
                output_image_path=img_path,
                execution_telemetry=telemetry,
            )
            ProvenanceManager.save_manifest(manifest, manifest_path)
            return manifest

        elif chosen_route == "kaggle_accelerator":
            # In Kaggle route, local orchestrator prepares the bundle and notes instructions
            raise JobExecutionError(
                f"Job '{job_bundle.job_id}' is configured for Kaggle accelerator execution. "
                "Run 'avatar prepare' to create the bundle, execute on Kaggle, then run 'avatar ingest' to import results."
            )

        elif chosen_route in {"local_cpu", "local_gpu"}:
            # Check if PyTorch and diffusers are available locally
            try:
                import torch
                from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            except ImportError:
                # If heavy ML packages are not installed locally on this non-GPU machine, fall back cleanly to mock or report block
                raise JobExecutionError(
                    f"Local ML engine ({chosen_route}) requested, but 'torch'/'diffusers' are not installed locally. "
                    "Use Kaggle GPU accelerator for inference or route='mock_runner' for local CPU testing."
                )

            # Local generation if dependencies are present
            start_time = time.time()
            device = "cuda" if chosen_route == "local_gpu" and torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32

            pipe = StableDiffusionPipeline.from_pretrained(
                job_bundle.metadata.model_repo,
                revision=job_bundle.metadata.model_revision,
                torch_dtype=dtype,
            )
            pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
            pipe = pipe.to(device)

            generator = torch.Generator(device=device).manual_seed(job_bundle.seed)
            result = pipe(
                prompt=job_bundle.prompts.positive_prompt,
                negative_prompt=job_bundle.prompts.negative_prompt,
                width=job_bundle.metadata.width,
                height=job_bundle.metadata.height,
                num_inference_steps=job_bundle.metadata.inference_steps,
                guidance_scale=job_bundle.metadata.guidance_scale,
                generator=generator,
            )

            image = result.images[0]
            image.save(img_path, format="PNG")
            duration = time.time() - start_time

            telemetry = {
                "engine": "diffusers_pipeline",
                "duration_sec": round(duration, 4),
                "device": str(device),
                "vram_peak_mb": round(torch.cuda.max_memory_allocated() / (1024 * 1024), 2) if device == "cuda" else 0.0,
            }

            manifest = ProvenanceManager.create_manifest(
                job_bundle=job_bundle,
                status="success",
                output_image_path=img_path,
                execution_telemetry=telemetry,
            )
            ProvenanceManager.save_manifest(manifest, manifest_path)
            return manifest

        else:
            raise JobExecutionError(f"Unknown compute route '{chosen_route}'.")
