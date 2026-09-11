"""
Job bundle management, serialization, and caching module for the Human Avatar System.
"""

import json
from pathlib import Path
import random
import shutil
from typing import Dict, List, Optional, Tuple
import zipfile

from avatar_system.config import SystemConfig, default_config
from avatar_system.exceptions import JobExecutionError, SafetyRefusalError, ValidationError
from avatar_system.prompts import PromptBuilder
from avatar_system.provenance import ProvenanceManager
from avatar_system.safety import SafetyEngine
from avatar_system.schemas import (
    AvatarSpec,
    JobBundle,
    JobMetadata,
    PromptBundle,
    ProvenanceManifest,
    SafetyResult,
)
from avatar_system.validator import OutputValidator


class JobManager:
    """Manages job bundle creation, validation, caching, and export packaging."""

    def __init__(
        self,
        config: Optional[SystemConfig] = None,
        safety_engine: Optional[SafetyEngine] = None,
        prompt_builder: Optional[PromptBuilder] = None,
    ):
        self.config = config or default_config
        self.config.ensure_directories()
        self.safety_engine = safety_engine or SafetyEngine()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def prepare_job(
        self,
        spec: AvatarSpec,
        model_repo: Optional[str] = None,
        model_revision: Optional[str] = None,
        inference_steps: int = 25,
        guidance_scale: float = 7.5,
        route: str = "kaggle_accelerator",
        force_seed: Optional[int] = None,
    ) -> JobBundle:
        """
        Validates specification, evaluates safety, assigns deterministic seed,
        and constructs a JobBundle.
        """
        # Step 1: Pre-generation Safety Evaluation
        safety_res = self.safety_engine.evaluate_spec(spec)
        if not safety_res.is_safe:
            raise SafetyRefusalError(
                f"Safety refusal for avatar '{spec.avatar_id}': {'; '.join(safety_res.refusal_reasons)}",
                refusal_reasons=safety_res.refusal_reasons,
            )

        # Step 2: Deterministic Seed Assignment
        if force_seed is not None:
            seed = force_seed
        elif spec.seed is not None:
            seed = spec.seed
        else:
            # Generate deterministic 32-bit positive integer seed
            seed = random.randint(100000, 4294967295)

        # Step 3: Modular Prompt Construction
        prompts = self.prompt_builder.build_prompt_bundle(spec)

        # Step 4: Dimension resolution
        width, height = spec.get_dimensions(base_dimension=512)

        job_id = f"job_{spec.avatar_id}_{seed}"
        metadata = JobMetadata(
            job_id=job_id,
            model_repo=model_repo or self.config.default_model_repo,
            model_revision=model_revision or self.config.default_model_revision,
            inference_steps=inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            seed=seed,
            route=route,
        )

        return JobBundle(
            job_id=job_id,
            avatar_spec=spec,
            prompts=prompts,
            safety_result=safety_res,
            seed=seed,
            metadata=metadata,
        )

    def write_job_bundle(self, bundle: JobBundle, target_dir: Optional[Path] = None) -> Path:
        """
        Serializes the job bundle into a portable self-contained folder.
        """
        job_dir = target_dir or (self.config.job_dir / bundle.job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        # 1. job.json (Master manifest)
        with open(job_dir / "job.json", "w", encoding="utf-8") as f:
            f.write(bundle.model_dump_json(indent=2))

        # 2. avatar_spec.json
        with open(job_dir / "avatar_spec.json", "w", encoding="utf-8") as f:
            f.write(bundle.avatar_spec.model_dump_json(indent=2))

        # 3. prompts.json
        with open(job_dir / "prompts.json", "w", encoding="utf-8") as f:
            f.write(bundle.prompts.model_dump_json(indent=2))

        # 4. seed.json
        with open(job_dir / "seed.json", "w", encoding="utf-8") as f:
            json.dump({"seed": bundle.seed, "job_id": bundle.job_id}, f, indent=2)

        # 5. safety_result.json
        with open(job_dir / "safety_result.json", "w", encoding="utf-8") as f:
            f.write(bundle.safety_result.model_dump_json(indent=2))

        # 6. README.txt
        readme_content = (
            f"Job Bundle: {bundle.job_id}\n"
            f"Avatar ID: {bundle.avatar_spec.avatar_id}\n"
            f"Deterministic Seed: {bundle.seed}\n"
            f"Target Model: {bundle.metadata.model_repo} (Revision: {bundle.metadata.model_revision})\n"
            f"Resolution: {bundle.metadata.width}x{bundle.metadata.height} (Aspect Ratio: {bundle.avatar_spec.aspect_ratio})\n"
            f"Inference Steps: {bundle.metadata.inference_steps}\n\n"
            "This bundle is portable and designed to be executed directly by the Kaggle\n"
            "accelerator worker notebook or local execution engine.\n"
        )
        with open(job_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)

        return job_dir

    def load_job_bundle(self, job_dir: Path) -> JobBundle:
        """Loads a JobBundle from a directory containing job.json."""
        job_file = job_dir / "job.json"
        if not job_file.exists():
            raise JobExecutionError(f"Invalid job bundle: missing {job_file}")
        with open(job_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JobBundle.model_validate(data)

    def package_jobs_to_zip(self, job_dirs: List[Path], output_zip_path: Path) -> Path:
        """Packages multiple job bundles into a single portable zip archive for Kaggle."""
        output_zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for jd in job_dirs:
                for file_path in jd.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(jd.parent)
                        zf.write(file_path, arcname)
        return output_zip_path

    def check_resume_cache(self, spec: AvatarSpec, seed: int, model_repo: str) -> Optional[ProvenanceManifest]:
        """
        Checks if a valid, uncorrupted output already exists matching the exact spec,
        seed, and model configuration.
        """
        expected_manifest_path = self.config.output_dir / f"{spec.avatar_id}_{seed}_manifest.json"
        if not expected_manifest_path.exists():
            return None

        val_res = OutputValidator.validate_manifest_and_image(expected_manifest_path)
        if not val_res.is_valid:
            return None

        manifest = ProvenanceManager.load_manifest(expected_manifest_path)
        # Check attribute match
        if (
            manifest.avatar_id == spec.avatar_id
            and manifest.seed == seed
            and manifest.model_name == model_repo
            and manifest.status == "success"
        ):
            return manifest

        return None
