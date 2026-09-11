"""
Unit tests for the OutputValidator (detects valid, corrupted, zero-byte, and mismatched images).
"""

from pathlib import Path
from PIL import Image
from avatar_system.job_manager import JobManager
from avatar_system.provenance import ProvenanceManager, compute_file_sha256
from avatar_system.schemas import AvatarSpec
from avatar_system.validator import OutputValidator


def test_validator_valid_image(valid_mock_png: Path):
    """Verifies that a valid PNG passes dimension and decoding validation."""
    res = OutputValidator.validate_image_file(
        valid_mock_png,
        expected_width=512,
        expected_height=512,
        expected_aspect_ratio="1:1",
    )
    assert res.is_valid is True
    assert len(res.errors) == 0
    assert res.image_properties["format"] == "PNG"


def test_validator_detects_corrupted_file(corrupted_image_file: Path):
    """Verifies that a non-decodable corrupted file is rejected."""
    res = OutputValidator.validate_image_file(corrupted_image_file)
    assert res.is_valid is False
    assert any("corrupted" in err.lower() or "failed" in err.lower() for err in res.errors)


def test_validator_detects_zero_byte_file(zero_byte_file: Path):
    """Verifies that an empty 0-byte file is rejected."""
    res = OutputValidator.validate_image_file(zero_byte_file)
    assert res.is_valid is False
    assert any("empty" in err.lower() or "0 bytes" in err.lower() for err in res.errors)


def test_validator_detects_dimension_mismatch(valid_mock_png: Path):
    """Verifies that unexpected dimensions are flagged."""
    res = OutputValidator.validate_image_file(
        valid_mock_png,
        expected_width=1024,
        expected_height=1024,
    )
    assert res.is_valid is False
    assert any("mismatch" in err.lower() for err in res.errors)


def test_validator_detects_hash_tampering(sample_avatar_spec: AvatarSpec, valid_mock_png: Path, tmp_path: Path):
    """Verifies that if an image file is altered after manifest creation, the mismatch is flagged."""
    mgr = JobManager()
    bundle = mgr.prepare_job(sample_avatar_spec, route="mock_runner")
    manifest = ProvenanceManager.create_manifest(
        job_bundle=bundle,
        status="success",
        output_image_path=valid_mock_png,
    )

    manifest_file = tmp_path / f"{sample_avatar_spec.avatar_id}_manifest.json"
    ProvenanceManager.save_manifest(manifest, manifest_file)

    # Tamper with image (change bytes)
    tampered_img_path = tmp_path / "tampered.png"
    img2 = Image.new("RGB", (512, 512), color=(255, 0, 0))
    img2.save(tampered_img_path, format="PNG")

    # Validate against tampered image
    val_res = OutputValidator.validate_manifest_and_image(manifest_file, image_path=tampered_img_path)
    assert val_res.is_valid is False
    assert any("hash mismatch" in err.lower() for err in val_res.errors)
