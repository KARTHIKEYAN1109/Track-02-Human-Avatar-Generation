"""
Provenance and manifest tracking module for the Human Avatar System.
Ensures full auditability, cryptographic hashing, and synthetic media labeling.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from typing import Any, Dict, Optional
import uuid

import pydantic
from avatar_system import __version__ as package_version
from avatar_system.schemas import (
    AvatarSpec,
    JobBundle,
    ProvenanceManifest,
    SafetyResult,
)


def compute_file_sha256(filepath: Path) -> str:
    """Calculates SHA256 hexadecimal digest for a given file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_runtime_software_versions() -> Dict[str, str]:
    """Captures runtime environment library versions."""
    versions = {
        "avatar_system": package_version,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pydantic": pydantic.__version__,
    }

    # Optional diffusers / torch versions if present
    for lib in ["torch", "diffusers", "transformers", "accelerate", "PIL"]:
        try:
            mod = __import__(lib)
            versions[lib] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pass

    return versions


class ProvenanceManager:
    """Creates, verifies, and serializes provenance manifests."""

    @staticmethod
    def create_manifest(
        job_bundle: JobBundle,
        status: str = "success",
        output_image_path: Optional[Path] = None,
        image_sha256: Optional[str] = None,
        execution_telemetry: Optional[Dict[str, Any]] = None,
        software_versions: Optional[Dict[str, str]] = None,
    ) -> ProvenanceManifest:
        """
        Builds a comprehensive ProvenanceManifest instance for an executed job.
        """
        output_filename = None
        computed_sha = image_sha256

        if output_image_path:
            p = Path(output_image_path)
            output_filename = p.name
            if p.exists() and not computed_sha:
                computed_sha = compute_file_sha256(p)

        manifest_id = f"man_{uuid.uuid4().hex[:12]}"
        now_utc = datetime.now(timezone.utc).isoformat()

        versions = software_versions or get_runtime_software_versions()
        telemetry = execution_telemetry or {}

        return ProvenanceManifest(
            manifest_id=manifest_id,
            job_id=job_bundle.job_id,
            avatar_id=job_bundle.avatar_spec.avatar_id,
            timestamp_utc=now_utc,
            status=status,
            avatar_spec=job_bundle.avatar_spec.model_dump(),
            positive_prompt=job_bundle.prompts.positive_prompt,
            negative_prompt=job_bundle.prompts.negative_prompt,
            seed=job_bundle.seed,
            model_name=job_bundle.metadata.model_repo,
            model_revision=job_bundle.metadata.model_revision,
            sampler_or_scheduler="DPMSolverMultistepScheduler",
            inference_steps=job_bundle.metadata.inference_steps,
            guidance_scale=job_bundle.metadata.guidance_scale,
            image_width=job_bundle.metadata.width,
            image_height=job_bundle.metadata.height,
            aspect_ratio=job_bundle.avatar_spec.aspect_ratio,
            output_filename=output_filename,
            image_sha256=computed_sha,
            synthetic_media=True,
            synthetic_label="AI-Generated Fictional Human Avatar",
            software_versions=versions,
            compute_route=job_bundle.metadata.route,
            safety_result=job_bundle.safety_result,
            execution_telemetry=telemetry,
        )

    @staticmethod
    def save_manifest(manifest: ProvenanceManifest, target_path: Path) -> None:
        """Saves manifest to disk as formatted JSON."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

    @staticmethod
    def load_manifest(manifest_path: Path) -> ProvenanceManifest:
        """Loads and parses a manifest from disk."""
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ProvenanceManifest.model_validate(data)
