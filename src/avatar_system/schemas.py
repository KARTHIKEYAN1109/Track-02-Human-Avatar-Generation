"""
Pydantic schemas for the Human Avatar System.
Defines strict contracts for avatar specifications, job bundles,
safety assessments, provenance manifests, and evaluation results.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class AvatarSpec(BaseModel):
    """
    Structured specification for an avatar portrait.
    Enforces inclusive appearance controls and separates nationality/cultural
    context from physical attributes.
    """
    avatar_id: str = Field(
        ...,
        description="Unique identifier for the avatar (alphanumeric, hyphens, underscores).",
        min_length=1,
        max_length=64,
    )
    age_band: str = Field(
        ...,
        description="Subject age band (e.g. young_adult, adult, middle_aged, senior).",
    )
    presentation: str = Field(
        ...,
        description="Presentation style (e.g. professional, casual, formal, creative, athletic, academic).",
    )
    skin_tone: str = Field(
        ...,
        description="Neutral skin tone descriptor (e.g. fair, light_olive, medium_warm, rich_bronze, deep_ebony).",
    )
    hair: str = Field(
        ...,
        description="Hair color (e.g. black, dark_brown, golden_blonde, auburn, silver_grey).",
    )
    hair_style: str = Field(
        ...,
        description="Hair style/cut (e.g. short_fade, shoulder_length_wavy, braided_locs, sleek_bob, afro_curls).",
    )
    attire: str = Field(
        ...,
        description="Clothing description (e.g. business_casual, business_suit, linen_shirt, crewneck_sweater).",
    )
    background: str = Field(
        ...,
        description="Environment/setting (e.g. neutral_studio, minimalist_modern_office, sunlit_library).",
    )
    pose: str = Field(
        default="front_facing_portrait",
        description="Pose / framing (e.g. front_facing_portrait, three_quarter_profile, relaxed_headshot).",
    )
    expression: str = Field(
        default="neutral_friendly",
        description="Facial expression (e.g. neutral, neutral_friendly, warm_smile, confident_calm).",
    )
    lighting: str = Field(
        default="soft_studio",
        description="Lighting scheme (e.g. soft_studio, natural_window_light, warm_rim_lighting).",
    )
    aspect_ratio: str = Field(
        default="1:1",
        description="Target image aspect ratio (1:1, 4:5, 16:9, 3:4).",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Deterministic integer seed (0 to 4294967295).",
    )
    cultural_context: Optional[str] = Field(
        default=None,
        description="Neutral geographic or cultural context note, kept decoupled from physical appearance.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional human-readable notes or description.",
    )
    reference_images: Optional[List[str]] = Field(
        default=None,
        description="Optional paths or URIs to reference images.",
    )
    consent_status: Literal["granted", "withheld", "not_applicable"] = Field(
        default="not_applicable",
        description="Consent verification status for personalized or reference generation.",
    )
    reference_rights_status: Literal["owned", "licensed", "public_domain", "unauthorized", "not_applicable"] = Field(
        default="not_applicable",
        description="Copyright / intellectual property rights status for supplied references.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional structured metadata or experiment tags.",
    )

    @field_validator("avatar_id")
    @classmethod
    def validate_avatar_id(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("avatar_id must contain only letters, numbers, underscores, and hyphens.")
        return v

    @field_validator("seed")
    @classmethod
    def validate_seed(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if not isinstance(v, int) or isinstance(v, bool):
                raise ValueError("seed must be an integer.")
            if v < 0 or v > 4294967295:
                raise ValueError("seed must be an unsigned 32-bit integer in range [0, 4294967295].")
        return v

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, v: str) -> str:
        valid_ratios = {"1:1", "4:5", "16:9", "3:4", "9:16", "5:4"}
        if v not in valid_ratios:
            raise ValueError(f"aspect_ratio '{v}' not supported. Supported: {sorted(list(valid_ratios))}")
        return v

    def get_dimensions(self, base_dimension: int = 512) -> tuple[int, int]:
        """Calculates width and height in pixels from the aspect ratio, rounded to multiples of 8."""
        ratio_map = {
            "1:1": (base_dimension, base_dimension),
            "4:5": (416, 512),
            "3:4": (384, 512),
            "5:4": (512, 416),
            "16:9": (512, 288),
            "9:16": (288, 512),
        }
        return ratio_map.get(self.aspect_ratio, (base_dimension, base_dimension))


class PromptBundle(BaseModel):
    """Encapsulates generated positive/negative prompts and attribute tags."""
    positive_prompt: str = Field(..., description="Full text-to-image positive prompt.")
    negative_prompt: str = Field(..., description="Full text-to-image negative prompt.")
    structured_clauses: Dict[str, str] = Field(
        default_factory=dict,
        description="Individual attribute clauses used to assemble the positive prompt.",
    )
    model_compatibility: str = Field(
        default="sd-1.5",
        description="Target model architecture for prompt styling.",
    )


class SafetyResult(BaseModel):
    """Outcome of pre-generation safety and consent validation."""
    is_safe: bool = Field(..., description="True if generation is permitted.")
    refusal_reasons: List[str] = Field(
        default_factory=list,
        description="Explanations if request was rejected.",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-blocking safety warnings or advisories.",
    )
    risk_score: float = Field(
        default=0.0,
        description="Estimated risk level between 0.0 (safe) and 1.0 (unsafe).",
    )
    checked_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of check.",
    )


class JobMetadata(BaseModel):
    """Job execution metadata and hyperparameters."""
    job_id: str = Field(...)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_repo: str = Field(default="stable-diffusion-v1-5/stable-diffusion-v1-5")
    model_revision: str = Field(default="main")
    inference_steps: int = Field(default=25, ge=1, le=100)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    width: int = Field(default=512)
    height: int = Field(default=512)
    seed: int = Field(...)
    route: Literal["local_cpu", "local_gpu", "kaggle_accelerator", "mock_runner"] = Field(
        default="kaggle_accelerator"
    )


class JobBundle(BaseModel):
    """Complete, self-contained portable job package."""
    job_id: str = Field(...)
    avatar_spec: AvatarSpec = Field(...)
    prompts: PromptBundle = Field(...)
    safety_result: SafetyResult = Field(...)
    seed: int = Field(...)
    metadata: JobMetadata = Field(...)


class ProvenanceManifest(BaseModel):
    """Comprehensive machine-readable provenance manifest for an avatar generation."""
    manifest_id: str = Field(..., description="Unique UUID or hash of manifest.")
    job_id: str = Field(..., description="Source job ID.")
    avatar_id: str = Field(..., description="Avatar identifier.")
    timestamp_utc: str = Field(..., description="Timestamp of generation in UTC ISO 8601.")
    status: Literal["success", "failed", "degraded", "refused"] = Field(...)
    
    # Specification and prompt snapshot
    avatar_spec: Dict[str, Any] = Field(...)
    positive_prompt: str = Field(...)
    negative_prompt: str = Field(...)
    
    # Generation parameters
    seed: int = Field(...)
    model_name: str = Field(...)
    model_revision: str = Field(...)
    sampler_or_scheduler: str = Field(default="DPMSolverMultistepScheduler")
    inference_steps: int = Field(...)
    guidance_scale: float = Field(...)
    image_width: int = Field(...)
    image_height: int = Field(...)
    aspect_ratio: str = Field(...)
    
    # Asset details
    output_filename: Optional[str] = Field(default=None)
    image_sha256: Optional[str] = Field(default=None)
    
    # Provenance & synthetic media disclosures
    synthetic_media: bool = Field(default=True)
    synthetic_label: str = Field(default="AI-Generated Fictional Human Avatar")
    software_versions: Dict[str, str] = Field(default_factory=dict)
    compute_route: str = Field(...)
    safety_result: SafetyResult = Field(...)
    execution_telemetry: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Result of image and manifest validation."""
    is_valid: bool = Field(...)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    image_properties: Dict[str, Any] = Field(default_factory=dict)
    manifest_verified: bool = Field(default=False)
