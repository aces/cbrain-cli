import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.data.tags import create_tag, delete_tag, list_tags, show_tag, update_tag
from tests.conftest import install_auth
from tests.conftest import make_args as _args


@pytest.fixture(autouse=True)
def _patch_locals():
    install_auth()


def _tag_args(**kwargs):
    return _args(name="mytag", user_id=1, group_id=2, **kwargs)


def test_list_tags_returns_list(mock_urlopen):
    mock_urlopen([{"id": 1, "name": "mytag"}])
    result = list_tags(_args())
    assert isinstance(result, list)
    assert result[0]["id"] == 1


def test_list_tags_empty_list_is_not_error(mock_urlopen):
    mock_urlopen([])
    assert list_tags(_args()) == []


def test_show_tag_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_tag(_args(id=None))


def test_show_tag_returns_dict(mock_urlopen):
    mock_urlopen({"id": 5, "name": "mytag"})
    result = show_tag(_args(id=5))
    assert result["id"] == 5


def test_create_tag_missing_name_raises():
    with pytest.raises(CliValidationError):
        create_tag(_args(name=None, user_id=1, group_id=2))


def test_create_tag_returns_tuple_on_success(mock_urlopen):
    mock_urlopen({"id": 7, "name": "mytag"}, status=201)
    data, success, error_msg, status = create_tag(_tag_args())
    assert success is True
    assert status == 201
    assert data["id"] == 7


def test_update_tag_missing_tag_id_raises():
    with pytest.raises(CliValidationError):
        update_tag(_tag_args(tag_id=None))


def test_update_tag_returns_tuple_on_success(mock_urlopen):
    mock_urlopen({"id": 7, "name": "updated"}, status=200)
    data, success, error_msg, status = update_tag(_tag_args(tag_id=7))
    assert success is True


def test_delete_tag_missing_tag_id_raises():
    with pytest.raises(CliValidationError):
        delete_tag(_args(tag_id=None))


def test_delete_tag_returns_tuple_on_success(mock_urlopen):
    mock_urlopen({}, status=200)
    success, error_msg, status = delete_tag(_args(tag_id=7))
    assert success is True
    assert status == 200
