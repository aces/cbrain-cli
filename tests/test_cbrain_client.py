import urllib.error

import pytest

from cbrain_cli.cli_utils import CbrainClient, CliApiError
from cbrain_cli.config import DEFAULT_TIMEOUT
from tests.conftest import TOKEN, URL, install_auth


@pytest.fixture
def client():
    return CbrainClient(URL, TOKEN, user_id=42)


def test_strips_trailing_slash():
    assert CbrainClient(f"{URL}/", TOKEN).base_url == URL


def test_default_timeout(client):
    assert client.timeout == DEFAULT_TIMEOUT


def test_custom_timeout():
    assert CbrainClient(URL, TOKEN, timeout=99).timeout == 99


def test_from_credentials():
    install_auth(user_id=7)
    c = CbrainClient.from_credentials()
    assert c.base_url == URL and c.token == TOKEN and c.user_id == 7


def test_get(client, capture_urlopen):
    configure, captured = capture_urlopen
    configure({"id": 1})
    assert client.get("/tools") == {"id": 1}
    assert captured["headers"].get("Authorization") == f"Bearer {TOKEN}"


def test_get_params(client, capture_urlopen):
    configure, captured = capture_urlopen
    configure(raw_body=b"[]")
    client.get("/tools", params={"page": "1"})
    assert "page=1" in captured["url"]


def test_get_wraps_http_error(client, capture_urlopen):
    configure, _ = capture_urlopen
    configure(side_effect=urllib.error.HTTPError(URL, 404, "Not Found", {}, None))
    with pytest.raises(CliApiError) as exc_info:
        client.get("/tools")
    assert exc_info.value.status == 404
    assert isinstance(exc_info.value.__cause__, urllib.error.HTTPError)


def test_send_post(client, capture_urlopen):
    configure, captured = capture_urlopen
    configure({"id": 5}, status=201)
    data, status = client.send("POST", "/tags", payload={"tag": {"name": "t"}})
    assert data == {"id": 5} and status == 201
    assert captured["headers"].get("Content-type") == "application/json"


def test_send_delete_empty_body(client, capture_urlopen):
    configure, captured = capture_urlopen
    configure(raw_body=b"")
    data, _ = client.send("DELETE", "/session")
    assert data == {} and captured["method"] == "DELETE"


def test_post_form(client, capture_urlopen):
    configure, captured = capture_urlopen
    configure({"cbrain_api_token": "tok"})
    result = client.post_form("/session", {"login": "u", "password": "p"})
    assert result["cbrain_api_token"] == "tok"
    assert b"login=u" in captured["data"]
    assert "Bearer" not in captured["headers"].get("Authorization", "")


def test_post_multipart(client, capture_urlopen):
    configure, captured = capture_urlopen
    configure({"id": 1}, status=201)
    data, status = client.post_multipart("/userfiles", b"body", "multipart/form-data; boundary=x")
    assert data == {"id": 1} and status == 201
    assert "multipart/form-data" in captured["headers"].get("Content-type", "")
    assert captured["headers"].get("Authorization") == f"Bearer {TOKEN}"
