import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.data.files import (
    copy_file,
    delete_file,
    list_files,
    move_file,
    show_file,
    upload_file,
)
from tests.conftest import make_args as _args
from tests.conftest import patch_module_locals


@pytest.fixture(autouse=True)
def _patch_locals(monkeypatch):
    patch_module_locals(monkeypatch, "cbrain_cli.data.files")


def test_show_file_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_file(_args(file=None))


def test_show_file_returns_dict(mock_urlopen):
    mock_urlopen({"id": 10, "name": "data.csv"})
    result = show_file(_args(file=10))
    assert result["id"] == 10


def test_list_files_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "name": "data.csv"}])
    result = list_files(_args())
    assert isinstance(result, list)


def test_list_files_empty_list_is_not_error(mock_urlopen):
    mock_urlopen([])
    assert list_files(_args()) == []


def test_list_files_passes_filter_params(monkeypatch):
    captured = {}

    def fake_urlopen(req):
        from unittest.mock import MagicMock

        captured["url"] = req.full_url
        cm = MagicMock()
        cm.__enter__.return_value.read.return_value = b"[]"
        cm.__exit__.return_value = False
        return cm

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    list_files(_args(group_id=5, dp_id=None, user_id=None, parent_id=None, file_type=None))
    assert "group_id=5" in captured["url"]


def test_delete_file_missing_id_raises():
    with pytest.raises(CliValidationError):
        delete_file(_args(file_id=None))


def test_delete_file_returns_data(mock_urlopen):
    mock_urlopen({"deleted": 1})
    result = delete_file(_args(file_id=10))
    assert result["deleted"] == 1


def test_upload_file_missing_path_raises(tmp_path):
    with pytest.raises(CliValidationError, match="[Ff]ile"):
        upload_file(_args(file_path=str(tmp_path / "nonexistent.txt"), data_provider=1, group_id=2))


def test_upload_file_missing_group_id_raises(tmp_path):
    f = tmp_path / "data.txt"
    f.write_text("hello")
    with pytest.raises(CliValidationError, match="[Gg]roup"):
        upload_file(_args(file_path=str(f), data_provider=1, group_id=None))


def test_copy_file_missing_file_ids_raises():
    with pytest.raises(CliValidationError):
        copy_file(_args(file_id=None, dp_id=1))


def test_copy_file_missing_dp_id_raises():
    with pytest.raises(CliValidationError):
        copy_file(_args(file_id=[10], dp_id=None))


def test_move_file_missing_file_ids_raises():
    with pytest.raises(CliValidationError):
        move_file(_args(file_id=None, dp_id=1))


def test_copy_file_returns_tuple(mock_urlopen):
    mock_urlopen({"moved": 1}, status=200)
    result = copy_file(_args(file_id=[10], dp_id=2))
    assert isinstance(result, tuple)


def test_move_file_returns_tuple(mock_urlopen):
    mock_urlopen({"moved": 1}, status=200)
    result = move_file(_args(file_id=[10], dp_id=2))
    assert isinstance(result, tuple)


def test_upload_file_success(monkeypatch, tmp_path):
    upload_path = tmp_path / "sample.bin"
    upload_path.write_bytes(b"payload")
    captured = {}

    def fake_urlopen(request):
        captured["content_type"] = request.headers.get("Content-type", "")
        from unittest.mock import MagicMock

        cm = MagicMock()
        cm.__enter__.return_value.read.return_value = b'{"id": 99, "notice": "ok"}'
        cm.__enter__.return_value.status = 201
        cm.__exit__.return_value = False
        return cm

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = upload_file(
        _args(file_path=str(upload_path), data_provider=1, group_id=2),
    )
    assert result[0]["id"] == 99
    assert result[2] == "sample.bin"
    assert "multipart/form-data" in captured["content_type"]
