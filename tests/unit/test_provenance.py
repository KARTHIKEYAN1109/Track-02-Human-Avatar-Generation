"""
Unit tests for provenance manifest generation, SHA256 hashing, and serialization.
"""

from pathlib import Path
from avatar_system.job_manager import JobManager
from avatar_system.provenance import ProvenanceManager, compute_file_sha256
from avatar_system.schemas import AvatarSpec, ProvenanceManifest


def test_sha256_computation(valid_mock_png: Path):
    """Verifies SHA256 checksum generation for a file."""
    sha = compute_file_sha256(valid_mock_png)
    assert isinstance(sha, str)
    assert len(sha) == 64


def test_provenance_manifest_creation_and_save(sample_avatar_spec: AvatarSpec, valid_mock_png: Path, tmp_path: Path):
    """Verifies that manifests serialize and deserialize cleanly."""
    mgr = JobManager()
    bundle = mgr.prepare_job(sample_avatar_spec, route="mock_runner")

    manifest = ProvenanceManager.create_manifest(
        job_bundle=bundle,
        status="success",
        output_image_path=valid_mock_png,
    )

    assert manifest.avatar_id == sample_avatar_spec.avatar_id
    assert manifest.seed == sample_avatar_spec.seed
    assert manifest.synthetic_media is True
    assert manifest.synthetic_label == "AI-Generated Fictional Human Avatar"
    assert manifest.image_sha256 is not None

    manifest_file = tmp_path / "test_manifest.json"
    ProvenanceManager.save_manifest(manifest, manifest_file)
    assert manifest_file.exists()

    loaded = ProvenanceManager.load_manifest(manifest_file)
    assert loaded.manifest_id == manifest.manifest_id
    assert loaded.seed == manifest.seed
    assert loaded.image_sha256 == manifest.image_sha256
