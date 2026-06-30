import urllib.error

import pytest

from cbrain_cli.cli_utils import api_get, api_post_form, api_send
from tests.conftest import TOKEN, URL


def test_api_get_returns_parsed_json(mock_urlopen):
    mock_urlopen({"id": 1, "name": "tool"})
    assert api_get(f"{URL}/tools", TOKEN) == {"id": 1, "name": "tool"}


def test_api_get_builds_query_string(capture_urlopen):
    """api_get appends params as a query string."""
    configure, captured = capture_urlopen
    configure(raw_body=b"[]")
    api_get(f"{URL}/tools", TOKEN, {"page": "1", "per_page": "25"})
    assert "page=1" in captured["url"]
    assert "per_page=25" in captured["url"]


def test_api_get_sends_authorization_header(capture_urlopen):
    configure, captured = capture_urlopen
    configure({})
    api_get(f"{URL}/tools", TOKEN)
    assert captured["headers"].get("Authorization") == f"Bearer {TOKEN}"


def test_api_get_propagates_http_error(capture_urlopen):
    configure, _captured = capture_urlopen
    configure(
        side_effect=urllib.error.HTTPError(URL, 404, "Not Found", {}, None),
    )
    with pytest.raises(urllib.error.HTTPError):
        api_get(f"{URL}/tools", TOKEN)


def test_api_post_form_returns_parsed_json(mock_urlopen):
    mock_urlopen({"cbrain_api_token": "tok", "user_id": 2})
    result = api_post_form(f"{URL}/session", {"login": "user", "password": "pass"})
    assert result["cbrain_api_token"] == "tok"


def test_api_post_form_sends_form_encoded_body(capture_urlopen):
    configure, captured = capture_urlopen
    configure({})
    api_post_form(f"{URL}/session", {"login": "admin", "password": "secret"})
    assert b"login=admin" in captured["data"]
    assert b"password=secret" in captured["data"]
    # no Bearer token in form post
    assert "Bearer" not in captured["headers"].get("Authorization", "")


def test_api_send_returns_parsed_json_and_status(mock_urlopen):
    mock_urlopen({"id": 5}, status=201)
    data, status = api_send(f"{URL}/tags", TOKEN, payload={"tag": {"name": "t"}})
    assert data == {"id": 5}
    assert status == 201


def test_api_send_empty_body_returns_empty_dict(capture_urlopen):
    """Empty response body must not raise JSONDecodeError."""
    configure, _captured = capture_urlopen
    configure(raw_body=b"")
    data, status = api_send(f"{URL}/session", TOKEN, method="DELETE")
    assert data == {}
    assert status == 200


def test_api_send_sets_content_type_for_json_payload(capture_urlopen):
    configure, captured = capture_urlopen
    configure({})
    api_send(f"{URL}/tags", TOKEN, payload={"tag": {}})
    assert captured["headers"].get("Content-type") == "application/json"


def test_api_send_propagates_http_error(capture_urlopen):
    configure, _captured = capture_urlopen
    configure(
        side_effect=urllib.error.HTTPError(URL, 500, "Error", {}, None),
    )
    with pytest.raises(urllib.error.HTTPError):
        api_send(f"{URL}/tags", TOKEN)
