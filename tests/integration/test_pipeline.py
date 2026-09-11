"""
Integration tests for the complete Avatar Generation Pipeline.
"""

from pathlib import Path
from avatar_system.config import SystemConfig
from avatar_system.evaluation import EvaluationEngine
from avatar_system.job_manager import JobManager
from avatar_system.provenance import ProvenanceManager
from avatar_system.routing import ExecutionRouter
from avatar_system.schemas import AvatarSpec
from avatar_system.validator import OutputValidator


def test_full_local_orchestration_pipeline(temp_test_env: SystemConfig):
    """
    Executes full pipeline:
    Spec -> Safety Check -> Job Preparation -> Mock Execution -> Manifest Generation -> Validation -> Evaluation
    """
    spec = AvatarSpec(
        avatar_id="pipeline_avatar_01",
        age_band="young_adult",
        presentation="creative",
        skin_tone="rich_bronze",
        hair="black",
        hair_style="braided_locs",
        attire="linen_shirt",
        background="sunlit_library",
        aspect_ratio="1:1",
        seed=654321,
    )

    # 1. Prepare Job
    mgr = JobManager(config=temp_test_env)
    bundle = mgr.prepare_job(spec, route="mock_runner")
    job_dir = mgr.write_job_bundle(bundle)
    assert (job_dir / "job.json").exists()

    # 2. Execute Job
    router = ExecutionRouter(config=temp_test_env)
    manifest = router.execute_job(bundle, route="mock_runner")
    assert manifest.status == "success"

    # 3. Validate Output
    manifest_path = temp_test_env.output_dir / f"{spec.avatar_id}_{spec.seed}_manifest.json"
    val_res = OutputValidator.validate_manifest_and_image(manifest_path)
    assert val_res.is_valid is True
    assert val_res.manifest_verified is True

    # 4. Evaluate Adherence & Provenance
    adh = EvaluationEngine.evaluate_prompt_adherence(manifest)
    assert adh["adherence_score"] > 0.8
