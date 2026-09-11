"""
Unit tests for modular prompt construction and attribute isolation.
"""

from avatar_system.prompts import PromptBuilder, DEFAULT_NEGATIVE_PROMPT
from avatar_system.schemas import AvatarSpec


def test_prompt_builder_basic(sample_avatar_spec: AvatarSpec):
    """Verifies that PromptBuilder generates complete positive and negative prompts."""
    builder = PromptBuilder()
    bundle = builder.build_prompt_bundle(sample_avatar_spec)

    assert "Fictional portrait" in bundle.positive_prompt
    assert "medium warm skin tone" in bundle.positive_prompt
    assert "short fade dark brown hair" in bundle.positive_prompt
    assert "business casual" in bundle.positive_prompt
    assert bundle.negative_prompt == DEFAULT_NEGATIVE_PROMPT
    assert "skin_tone" in bundle.structured_clauses
    assert "hair" in bundle.structured_clauses


def test_prompt_builder_attribute_independence():
    """Verifies that changing a single attribute only affects its specific clause."""
    builder = PromptBuilder()

    spec1 = AvatarSpec(
        avatar_id="s1", age_band="adult", presentation="professional", skin_tone="fair",
        hair="dark_brown", hair_style="short_fade", attire="business_suit",
        background="neutral_studio", seed=100
    )
    spec2 = AvatarSpec(
        avatar_id="s2", age_band="adult", presentation="professional", skin_tone="deep_ebony",
        hair="dark_brown", hair_style="short_fade", attire="business_suit",
        background="neutral_studio", seed=100
    )

    b1 = builder.build_prompt_bundle(spec1)
    b2 = builder.build_prompt_bundle(spec2)

    assert "fair skin tone" in b1.positive_prompt
    assert "deep ebony skin tone" in b2.positive_prompt
    # All other structured clauses must be identical
    assert b1.structured_clauses["hair"] == b2.structured_clauses["hair"]
    assert b1.structured_clauses["attire"] == b2.structured_clauses["attire"]
    assert b1.structured_clauses["background"] == b2.structured_clauses["background"]


def test_prompt_builder_custom_negative(sample_avatar_spec: AvatarSpec):
    """Verifies custom negative prompt override."""
    builder = PromptBuilder()
    custom_neg = "ugly, blurry, low-res"
    bundle = builder.build_prompt_bundle(sample_avatar_spec, custom_negative=custom_neg)
    assert bundle.negative_prompt == custom_neg
