"""
End-to-end tests for multi-avatar batch generation, reproducibility, and export packaging.
"""

from pathlib import Path
from avatar_system.benchmark import BenchmarkRunner
from avatar_system.config import SystemConfig
from avatar_system.job_manager import JobManager
from avatar_system.routing import ExecutionRouter
from avatar_system.schemas import AvatarSpec
from avatar_system.validator import OutputValidator


def test_e2e_batch_generation_and_determinism(temp_test_env: SystemConfig):
    """
    Tests end-to-end multi-avatar generation with deterministic seeds.
    Verifies that running the same job twice with the same seed reproduces the exact same image and SHA256 checksum.
    """
    spec = AvatarSpec(
        avatar_id="determinism_test_01",
        age_band="adult",
        presentation="professional",
        skin_tone="medium_warm",
        hair="dark_brown",
        hair_style="short_fade",
        attire="business_casual",
        background="neutral_studio",
        aspect_ratio="1:1",
        seed=888888,
    )

    mgr = JobManager(config=temp_test_env)
    router = ExecutionRouter(config=temp_test_env)

    # Run Batch 1
    bundle1 = mgr.prepare_job(spec, route="mock_runner")
    manifest1 = router.execute_job(bundle1, route="mock_runner")
    sha1 = manifest1.image_sha256

    # Run Batch 2 (Identical parameters and seed)
    bundle2 = mgr.prepare_job(spec, route="mock_runner")
    manifest2 = router.execute_job(bundle2, route="mock_runner")
    sha2 = manifest2.image_sha256

    # Verify deterministic reproducibility
    assert sha1 == sha2
    assert manifest1.seed == manifest2.seed == 888888


def test_e2e_benchmark_execution(temp_test_env: SystemConfig):
    """
    Executes automated benchmark across test environment and verifies results structure.
    """
    runner = BenchmarkRunner(config=temp_test_env)
    results = runner.run_benchmark(save_results=True)

    assert results["successful_jobs"] > 0
    assert results["job_success_rate"] == 1.0
    assert results["latency_metrics"]["throughput_jobs_per_sec"] > 0
    assert (temp_test_env.evidence_dir / "benchmarks" / "benchmark_results.json").exists()
