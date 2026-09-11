"""
Unit tests for the SafetyEngine, likeness prevention, and consent validation.
"""

from avatar_system.safety import SafetyEngine
from avatar_system.schemas import AvatarSpec


def test_safety_pass_for_fictional_avatar(sample_avatar_spec: AvatarSpec):
    """Verifies that standard fictional avatars pass all safety checks."""
    engine = SafetyEngine()
    result = engine.evaluate_spec(sample_avatar_spec)
    assert result.is_safe is True
    assert len(result.refusal_reasons) == 0
    assert result.risk_score == 0.0


def test_safety_refusal_for_celebrity_likeness():
    """Verifies refusal when a known public figure's likeness is requested."""
    engine = SafetyEngine()
    spec = AvatarSpec(
        avatar_id="unsafe_01",
        age_band="adult",
        presentation="executive",
        skin_tone="fair",
        hair="brown",
        hair_style="short",
        attire="suit",
        background="studio",
        cultural_context="portrait of Elon Musk presenting at keynote",
    )
    result = engine.evaluate_spec(spec)
    assert result.is_safe is False
    assert any("Unauthorized Likeness" in r for r in result.refusal_reasons)
    assert result.risk_score >= 1.0


def test_safety_refusal_for_deepfake_intent():
    """Verifies refusal when deceptive deepfake patterns are present."""
    engine = SafetyEngine()
    spec = AvatarSpec(
        avatar_id="unsafe_02",
        age_band="adult",
        presentation="casual",
        skin_tone="medium_warm",
        hair="black",
        hair_style="short",
        attire="shirt",
        background="studio",
        notes="create a deepfake identical clone of the target person",
    )
    result = engine.evaluate_spec(spec)
    assert result.is_safe is False
    assert any("Deceptive Synthesis" in r for r in result.refusal_reasons)


def test_safety_refusal_for_unconsented_reference():
    """Verifies refusal when reference images lack explicit granted consent."""
    engine = SafetyEngine()
    spec = AvatarSpec(
        avatar_id="ref_test",
        age_band="adult",
        presentation="professional",
        skin_tone="fair",
        hair="blonde",
        hair_style="short",
        attire="suit",
        background="studio",
        reference_images=["path/to/unauthorized.jpg"],
        consent_status="withheld",
        reference_rights_status="unauthorized",
    )
    result = engine.evaluate_spec(spec)
    assert result.is_safe is False
    assert any("Consent Violation" in r for r in result.refusal_reasons)


def test_safety_pass_for_consented_reference():
    """Verifies approval when reference images have verified consent and owned rights."""
    engine = SafetyEngine()
    spec = AvatarSpec(
        avatar_id="ref_consented",
        age_band="adult",
        presentation="professional",
        skin_tone="fair",
        hair="blonde",
        hair_style="short",
        attire="suit",
        background="studio",
        reference_images=["path/to/consented.jpg"],
        consent_status="granted",
        reference_rights_status="owned",
    )
    result = engine.evaluate_spec(spec)
    assert result.is_safe is True
    assert len(result.refusal_reasons) == 0
