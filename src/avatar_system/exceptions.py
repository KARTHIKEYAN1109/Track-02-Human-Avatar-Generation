"""
Exception hierarchy for the Human Avatar System.
Ensures informative error messages and distinct exit codes.
"""

class AvatarSystemError(Exception):
    """Base exception for all domain errors in Avatar System."""
    exit_code: int = 1


class ValidationError(AvatarSystemError):
    """Raised when an avatar specification or schema is invalid."""
    exit_code: int = 2


class SafetyRefusalError(AvatarSystemError):
    """Raised when a request is refused due to safety, consent, or likeness violations."""
    exit_code: int = 3

    def __init__(self, message: str, refusal_reasons: list[str] = None):
        super().__init__(message)
        self.refusal_reasons = refusal_reasons or [message]


class ProvenanceError(AvatarSystemError):
    """Raised when provenance, manifest, or checksum verification fails."""
    exit_code: int = 4


class OutputCorruptedError(AvatarSystemError):
    """Raised when an output image is missing, empty, or unreadable."""
    exit_code: int = 5


class JobExecutionError(AvatarSystemError):
    """Raised when job packaging, dispatch, or inference execution fails."""
    exit_code: int = 6


class ConfigurationError(AvatarSystemError):
    """Raised when system configuration or directory structure is invalid."""
    exit_code: int = 7
