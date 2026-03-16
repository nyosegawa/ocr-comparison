"""Shared fixtures for evaluation tests."""

from __future__ import annotations

import pytest
from PIL import Image


@pytest.fixture
def small_rgb_image() -> Image.Image:
    """A small 100x50 red RGB image for testing."""
    return Image.new("RGB", (100, 50), color=(255, 0, 0))


@pytest.fixture
def small_rgba_image() -> Image.Image:
    """A small 100x50 RGBA image for testing."""
    return Image.new("RGBA", (100, 50), color=(255, 0, 0, 128))
