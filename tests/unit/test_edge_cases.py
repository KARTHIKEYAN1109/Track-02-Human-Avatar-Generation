"""
Edge case and failure mode tests for the Human Avatar System.
"""

from pathlib import Path
import pytest
from avatar_system.exceptions import ConfigurationError, JobExecutionError, SafetyRefusalError, ValidationError
from avatar_system.job_manager import JobManager
from avatar_system.routing import ExecutionRouter
from avatar_system.safety import SafetyEngine
from avatar_system.schemas import AvatarSpec
from avatar_system.validator import OutputValidator


def test_safety_raw_text_checks():
    """Verifies evaluate_text method for raw text inputs."""
    engine = SafetyEngine()
    safe, reasons = engine.evaluate_text("portrait of an architect in office")
    assert safe is True

    unsafe, reasons = engine.evaluate_text("portrait of Donald Trump speaking")
    assert unsafe is False
    assert len(reasons) > 0


def test_validator_missing_manifest():
    """Verifies validator behavior on non-existent manifest."""
    res = OutputValidator.validate_manifest_and_image(Path("non_existent_manifest.json"))
    assert res.is_valid is False
    assert "does not exist" in res.errors[0]


def test_validator_corrupted_manifest_json(tmp_path: Path):
    """Verifies validator handling of malformed JSON in manifest file."""
    bad_manifest = tmp_path / "bad_manifest.json"
    bad_manifest.write_text("{invalid json content:", encoding="utf-8")

    res = OutputValidator.validate_manifest_and_image(bad_manifest)
    assert res.is_valid is False
    assert "schema validation failed" in res.errors[0]


def test_router_invalid_route(sample_avatar_spec: AvatarSpec):
    """Verifies error on unrecognized execution route."""
    mgr = JobManager()
    bundle = mgr.prepare_job(sample_avatar_spec)
    router = ExecutionRouter()

    with pytest.raises(JobExecutionError):
        router.execute_job(bundle, route="invalid_compute_backend")


def test_router_kaggle_route_direct_run_exception(sample_avatar_spec: AvatarSpec):
    """Verifies that attempting direct local run on kaggle route prompts bundle preparation."""
    mgr = JobManager()
    bundle = mgr.prepare_job(sample_avatar_spec, route="kaggle_accelerator")
    router = ExecutionRouter()

    with pytest.raises(JobExecutionError) as exc_info:
        router.execute_job(bundle, route="kaggle_accelerator")
    assert "configured for Kaggle accelerator" in str(exc_info.value)
