from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from participium.services.storage_service import (
    LocalFileStorageService,
    StorageService,
)


# -------------------------
# Tests: StorageService
# -------------------------

def test_storage_service_save(capsys):
    service = StorageService()

    file = MagicMock()

    result = service.save(file)

    captured = capsys.readouterr()

    assert result == "simulated-file"
    assert "Simulating file storage operation." in captured.out


# -------------------------
# Tests: LocalFileStorageService
# -------------------------

def test_local_storage_creates_directory(tmp_path):
    media_root = tmp_path / "uploads"

    LocalFileStorageService(media_root)

    assert media_root.exists()
    assert media_root.is_dir()


@patch("participium.services.storage_service.uuid4")
def test_local_storage_save(mock_uuid, tmp_path):
    mock_uuid.return_value.hex = "abc123"

    media_root = tmp_path / "uploads"

    service = LocalFileStorageService(media_root)

    uploaded_file = MagicMock()
    uploaded_file.filename = "my image.jpg"

    result = service.save(uploaded_file)

    expected_name = "abc123_my_image.jpg"
    expected_path = media_root / expected_name

    assert result == expected_name

    uploaded_file.save.assert_called_once_with(expected_path)


@patch("participium.services.storage_service.uuid4")
def test_local_storage_save_without_filename(mock_uuid, tmp_path):
    mock_uuid.return_value.hex = "xyz999"

    media_root = tmp_path / "uploads"

    service = LocalFileStorageService(media_root)

    uploaded_file = MagicMock()
    uploaded_file.filename = None

    result = service.save(uploaded_file)

    assert result == "xyz999_attachment.bin"