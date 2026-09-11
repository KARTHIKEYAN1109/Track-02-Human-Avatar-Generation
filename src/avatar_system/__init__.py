"""
Avatar System: Open-Source AI Human-Avatar Generation System (Track 02).
"""

__version__ = "0.1.0"
__author__ = "SASTRA 2027 Graduate Hiring Candidate (Incubrix)"

from avatar_system.schemas import (
    AvatarSpec,
    JobBundle,
    ProvenanceManifest,
    SafetyResult,
    ValidationResult,
)
from avatar_system.prompts import PromptBuilder
from avatar_system.safety import SafetyEngine
from avatar_system.provenance import ProvenanceManager
from avatar_system.validator import OutputValidator
from avatar_system.job_manager import JobManager

__all__ = [
    "AvatarSpec",
    "JobBundle",
    "ProvenanceManifest",
    "SafetyResult",
    "ValidationResult",
    "PromptBuilder",
    "SafetyEngine",
    "ProvenanceManager",
    "OutputValidator",
    "JobManager",
]
