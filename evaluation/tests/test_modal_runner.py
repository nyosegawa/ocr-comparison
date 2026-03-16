"""Tests for src/models/modal_runner.py — Modal subprocess runner."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models.modal_runner import (
    MODAL_SCRIPTS_DIR,
    HunyuanOCRModal,
    ModalOCRModel,
    NDLOCRLiteModal,
)


class TestModalScriptsDir:
    def test_points_to_modal_scripts(self):
        assert MODAL_SCRIPTS_DIR.name == "modal_scripts"

    def test_common_py_exists(self):
        assert (MODAL_SCRIPTS_DIR / "_common.py").exists()


class TestModalOCRModelIsAvailable:
    def test_available_when_modal_cli_works(self):
        model = HunyuanOCRModal()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            assert model.is_available() is True

    def test_unavailable_when_modal_cli_fails(self):
        model = HunyuanOCRModal()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            assert model.is_available() is False

    def test_unavailable_when_modal_not_installed(self):
        model = HunyuanOCRModal()
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert model.is_available() is False

    def test_unavailable_on_timeout(self):
        model = HunyuanOCRModal()
        import subprocess
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("modal", 10)):
            assert model.is_available() is False


class TestModalModelAttributes:
    def test_hunyuan(self):
        m = HunyuanOCRModal()
        assert m.name == "hunyuan-ocr"
        assert m.category == "modal"
        assert m.script_name == "hunyuan_ocr.py"
        assert m.gpu == "L4"

    def test_ndlocr_lite_cpu(self):
        m = NDLOCRLiteModal()
        assert m.gpu == ""  # CPU-only


@pytest.mark.asyncio
class TestModalRecognizeBatch:
    async def test_successful_batch(self, small_rgb_image):
        model = HunyuanOCRModal()

        def mock_subprocess_run(cmd, **kwargs):
            # Write fake output to the output file
            output_path = cmd[cmd.index("--output") + 1]
            with open(output_path, "w") as f:
                json.dump({"results": ["recognized text"]}, f)

            class FakeResult:
                returncode = 0
                stdout = ""
                stderr = ""
            return FakeResult()

        with patch("src.models.modal_runner.subprocess.run", side_effect=mock_subprocess_run):
            results = await model.recognize_batch([small_rgb_image])
            assert results == ["recognized text"]

    async def test_failed_subprocess_raises(self, small_rgb_image):
        model = HunyuanOCRModal()

        class FakeResult:
            returncode = 1
            stdout = "some output"
            stderr = "error occurred"

        with patch("src.models.modal_runner.subprocess.run", return_value=FakeResult()):
            with pytest.raises(RuntimeError, match="Modal run failed"):
                await model.recognize_batch([small_rgb_image])

    async def test_recognize_delegates_to_batch(self, small_rgb_image):
        model = HunyuanOCRModal()

        def mock_subprocess_run(cmd, **kwargs):
            output_path = cmd[cmd.index("--output") + 1]
            with open(output_path, "w") as f:
                json.dump({"results": ["single result"]}, f)

            class FakeResult:
                returncode = 0
                stdout = ""
                stderr = ""
            return FakeResult()

        with patch("src.models.modal_runner.subprocess.run", side_effect=mock_subprocess_run):
            result = await model.recognize(small_rgb_image)
            assert result == "single result"
