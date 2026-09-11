"""
Unit tests for JobManager (bundle creation, packaging, and cache handling).
"""

from pathlib import Path
from avatar_system.config import SystemConfig
from avatar_system.job_manager import JobManager
from avatar_system.schemas import AvatarSpec


def test_prepare_and_write_job_bundle(sample_avatar_spec: AvatarSpec, temp_test_env: SystemConfig):
    """Verifies that JobManager creates all required bundle files."""
    mgr = JobManager(config=temp_test_env)
    bundle = mgr.prepare_job(sample_avatar_spec)
    job_dir = mgr.write_job_bundle(bundle)

    assert (job_dir / "job.json").exists()
    assert (job_dir / "avatar_spec.json").exists()
    assert (job_dir / "prompts.json").exists()
    assert (job_dir / "seed.json").exists()
    assert (job_dir / "safety_result.json").exists()
    assert (job_dir / "README.txt").exists()

    loaded = mgr.load_job_bundle(job_dir)
    assert loaded.job_id == bundle.job_id
    assert loaded.seed == bundle.seed


def test_job_manager_deterministic_seed():
    """Verifies that seed is deterministic when explicitly given and auto-assigned if absent."""
    mgr = JobManager()

    spec_with_seed = AvatarSpec(
        avatar_id="s1", age_band="adult", presentation="casual", skin_tone="fair",
        hair="black", hair_style="short", attire="shirt", background="studio",
        seed=777777
    )
    b1 = mgr.prepare_job(spec_with_seed)
    assert b1.seed == 777777

    spec_no_seed = AvatarSpec(
        avatar_id="s2", age_band="adult", presentation="casual", skin_tone="fair",
        hair="black", hair_style="short", attire="shirt", background="studio"
    )
    b2 = mgr.prepare_job(spec_no_seed)
    assert isinstance(b2.seed, int)
    assert b2.seed > 0


def test_package_jobs_to_zip(sample_avatar_spec: AvatarSpec, temp_test_env: SystemConfig, tmp_path: Path):
    """Verifies bundling multiple jobs into a portable zip file."""
    mgr = JobManager(config=temp_test_env)
    b1 = mgr.prepare_job(sample_avatar_spec)
    dir1 = mgr.write_job_bundle(b1)

    zip_path = tmp_path / "test_jobs.zip"
    mgr.package_jobs_to_zip([dir1], zip_path)
    assert zip_path.exists()
    assert zip_path.stat().st_size > 0
