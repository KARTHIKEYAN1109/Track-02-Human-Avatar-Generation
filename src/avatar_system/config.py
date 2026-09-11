"""
Configuration module for the Human Avatar System.
Provides strongly-typed settings and directory path resolvers.
"""

from pathlib import Path
import os
from typing import Optional


class SystemConfig:
    """System runtime configuration."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config_dir: Optional[Path] = None,
        job_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        evidence_dir: Optional[Path] = None,
        log_dir: Optional[Path] = None,
        default_model_repo: Optional[str] = None,
        default_model_revision: Optional[str] = None,
        default_device: Optional[str] = None,
        log_level: Optional[str] = None,
    ):
        # Resolve project root
        if project_root:
            self.project_root = Path(project_root).resolve()
        else:
            env_root = os.getenv("AVATAR_PROJECT_ROOT")
            if env_root:
                self.project_root = Path(env_root).resolve()
            else:
                # Default to three levels up from this file (human_avatar_system/)
                self.project_root = Path(__file__).resolve().parent.parent.parent

        self.config_dir = self._resolve_path(config_dir, "AVATAR_CONFIG_DIR", "configs")
        self.job_dir = self._resolve_path(job_dir, "AVATAR_JOB_DIR", "jobs")
        self.output_dir = self._resolve_path(output_dir, "AVATAR_OUTPUT_DIR", "outputs")
        self.evidence_dir = self._resolve_path(evidence_dir, "AVATAR_EVIDENCE_DIR", "evidence")
        self.log_dir = self._resolve_path(log_dir, "AVATAR_LOG_DIR", "evidence/logs")

        self.default_model_repo = (
            default_model_repo
            or os.getenv("AVATAR_DEFAULT_MODEL_REPO")
            or "stable-diffusion-v1-5/stable-diffusion-v1-5"
        )
        self.default_model_revision = (
            default_model_revision
            or os.getenv("AVATAR_DEFAULT_MODEL_REVISION")
            or "main"
        )
        self.default_device = (
            default_device
            or os.getenv("AVATAR_DEFAULT_DEVICE")
            or "auto"
        )
        self.log_level = (
            log_level
            or os.getenv("AVATAR_LOG_LEVEL")
            or "INFO"
        )

    def _resolve_path(self, override: Optional[Path], env_var: str, default_subpath: str) -> Path:
        if override:
            p = Path(override)
        elif os.getenv(env_var):
            p = Path(os.environ[env_var])
        else:
            p = self.project_root / default_subpath

        if not p.is_absolute():
            p = (self.project_root / p).resolve()
        return p

    def ensure_directories(self) -> None:
        """Ensure all required runtime directories exist."""
        for d in [
            self.config_dir,
            self.job_dir,
            self.output_dir,
            self.evidence_dir,
            self.log_dir,
            self.evidence_dir / "baseline",
            self.evidence_dir / "strong",
            self.evidence_dir / "failures",
            self.evidence_dir / "tests",
            self.evidence_dir / "benchmarks",
            self.evidence_dir / "manifests",
        ]:
            d.mkdir(parents=True, exist_ok=True)


# Default global instance
default_config = SystemConfig()
