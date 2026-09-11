"""
Unit tests for avatar specifications and Pydantic schemas.
"""

import pytest
from pydantic import ValidationError
from avatar_system.schemas import AvatarSpec, PromptBundle, SafetyResult, JobBundle, ProvenanceManifest


def test_avatar_spec_valid_instantiation(sample_avatar_spec: AvatarSpec):
    """Verifies that a well-formed spec instantiates cleanly."""
    assert sample_avatar_spec.avatar_id == "test_avatar_001"
    assert sample_avatar_spec.age_band == "adult"
    assert sample_avatar_spec.aspect_ratio == "1:1"
    assert sample_avatar_spec.seed == 123456


def test_avatar_spec_invalid_id_characters():
    """Verifies that invalid characters in avatar_id trigger validation error."""
    with pytest.raises(ValidationError):
        AvatarSpec(
            avatar_id="invalid avatar with spaces!",
            age_band="adult",
            presentation="casual",
            skin_tone="fair",
            hair="black",
            hair_style="short",
            attire="shirt",
            background="studio",
        )


def test_avatar_spec_negative_seed():
    """Verifies that negative seeds are rejected."""
    with pytest.raises(ValidationError):
        AvatarSpec(
            avatar_id="valid_id",
            age_band="adult",
            presentation="casual",
            skin_tone="fair",
            hair="black",
            hair_style="short",
            attire="shirt",
            background="studio",
            seed=-500,
        )


def test_avatar_spec_unsupported_aspect_ratio():
    """Verifies that invalid aspect ratios are rejected."""
    with pytest.raises(ValidationError):
        AvatarSpec(
            avatar_id="valid_id",
            age_band="adult",
            presentation="casual",
            skin_tone="fair",
            hair="black",
            hair_style="short",
            attire="shirt",
            background="studio",
            aspect_ratio="100:1",
        )


def test_avatar_spec_get_dimensions():
    """Verifies dimension mapping for supported aspect ratios."""
    spec_square = AvatarSpec(
        avatar_id="sq", age_band="adult", presentation="casual", skin_tone="fair",
        hair="black", hair_style="short", attire="shirt", background="studio",
        aspect_ratio="1:1"
    )
    assert spec_square.get_dimensions(512) == (512, 512)

    spec_portrait = AvatarSpec(
        avatar_id="port", age_band="adult", presentation="casual", skin_tone="fair",
        hair="black", hair_style="short", attire="shirt", background="studio",
        aspect_ratio="4:5"
    )
    w, h = spec_portrait.get_dimensions(512)
    assert w == 416
    assert h == 512
