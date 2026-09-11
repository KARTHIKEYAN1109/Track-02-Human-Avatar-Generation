"""
Unit tests for the EvaluationEngine (adherence, diversity metrics, and controlled attribute changes).
"""

from avatar_system.evaluation import EvaluationEngine
from avatar_system.job_manager import JobManager
from avatar_system.provenance import ProvenanceManager
from avatar_system.schemas import AvatarSpec


def test_prompt_adherence_evaluation(sample_avatar_spec: AvatarSpec):
    """Verifies calculation of prompt adherence score."""
    mgr = JobManager()
    bundle = mgr.prepare_job(sample_avatar_spec)
    manifest = ProvenanceManager.create_manifest(job_bundle=bundle)

    adh = EvaluationEngine.evaluate_prompt_adherence(manifest)
    assert adh["adherence_score"] > 0.8
    assert adh["matched_attributes"] >= 6


def test_batch_diversity_evaluation():
    """Verifies diversity scoring across multiple varied avatar specs."""
    mgr = JobManager()
    specs = [
        AvatarSpec(avatar_id="a1", age_band="young_adult", presentation="casual", skin_tone="fair", hair="blonde", hair_style="fade", attire="shirt", background="studio"),
        AvatarSpec(avatar_id="a2", age_band="adult", presentation="formal", skin_tone="deep_ebony", hair="black", hair_style="locs", attire="suit", background="office"),
        AvatarSpec(avatar_id="a3", age_band="senior", presentation="creative", skin_tone="medium_warm", hair="grey", hair_style="bob", attire="blazer", background="library"),
    ]
    manifests = [ProvenanceManager.create_manifest(job_bundle=mgr.prepare_job(s)) for s in specs]

    div = EvaluationEngine.evaluate_batch_diversity(manifests)
    assert div["total_avatars_evaluated"] == 3
    assert div["unique_skin_tones_count"] == 3
    assert div["unique_age_bands_count"] == 3
    assert div["overall_diversity_score"] == 1.0


def test_controlled_attribute_verification():
    """Verifies that controlled tests correctly validate that only the target attribute changed."""
    mgr = JobManager()
    base_spec = AvatarSpec(
        avatar_id="base", age_band="adult", presentation="formal", skin_tone="fair",
        hair="black", hair_style="short", attire="suit", background="studio", seed=100
    )
    variant_spec = AvatarSpec(
        avatar_id="var", age_band="adult", presentation="formal", skin_tone="deep_ebony",
        hair="black", hair_style="short", attire="suit", background="studio", seed=100
    )

    m_base = ProvenanceManager.create_manifest(job_bundle=mgr.prepare_job(base_spec))
    m_var = ProvenanceManager.create_manifest(job_bundle=mgr.prepare_job(variant_spec))

    # Check valid controlled test on skin_tone
    eval_res = EvaluationEngine.evaluate_controlled_attribute_change(m_base, m_var, "skin_tone")
    assert eval_res["strictly_controlled"] is True
    assert eval_res["target_attribute_changed"] is True
    assert len(eval_res["unintended_changes"]) == 0
