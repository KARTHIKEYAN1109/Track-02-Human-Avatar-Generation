"""
Pytest configuration and shared fixtures for the Human Avatar System test suite.
"""

from pathlib import Path
import shutil
import pytest
from PIL import Image

from avatar_system.config import SystemConfig
from avatar_system.schemas import AvatarSpec


@pytest.fixture
def sample_avatar_spec() -> AvatarSpec:
    """Provides a valid baseline fictional avatar specification."""
    return AvatarSpec(
        avatar_id="test_avatar_001",
        age_band="adult",
        presentation="professional",
        skin_tone="medium_warm",
        hair="dark_brown",
        hair_style="short_fade",
        attire="business_casual",
        background="neutral_studio",
        pose="front_facing_portrait",
        expression="neutral_friendly",
        lighting="soft_studio",
        aspect_ratio="1:1",
        seed=123456,
        cultural_context="contemporary urban workplace",
        notes="Standard unit test fixture.",
    )


@pytest.fixture
def temp_test_env(tmp_path: Path) -> SystemConfig:
    """Provides a temporary isolated SystemConfig environment."""
    test_root = tmp_path / "avatar_test_workspace"
    test_root.mkdir(parents=True, exist_ok=True)
    cfg = SystemConfig(project_root=test_root)
    cfg.ensure_directories()
    return cfg


@pytest.fixture
def valid_mock_png(tmp_path: Path) -> Path:
    """Creates a valid 512x512 RGB PNG image for testing."""
    img_path = tmp_path / "test_valid.png"
    img = Image.new("RGB", (512, 512), color=(120, 140, 160))
    img.save(img_path, format="PNG")
    return img_path


@pytest.fixture
def corrupted_image_file(tmp_path: Path) -> Path:
    """Creates a corrupted non-image file with a .png extension."""
    bad_path = tmp_path / "corrupted.png"
    with open(bad_path, "wb") as f:
        f.write(b"NOT_A_REAL_PNG_HEADER_CORRUPTED_BYTES_1234567890")
    return bad_path


@pytest.fixture
def zero_byte_file(tmp_path: Path) -> Path:
    """Creates an empty 0-byte file."""
    empty_path = tmp_path / "empty.png"
    empty_path.touch()
    return empty_path
