import importlib
from pathlib import Path

from tests.conftest import patch_module_locals, run_main


def test_main_invalid_pagination_skips_network(monkeypatch):
    urlopen_called = []

    def fake_urlopen(*_args, **_kwargs):
        urlopen_called.append(True)
        raise AssertionError("urlopen must not be called for invalid pagination")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = run_main(monkeypatch, ["cbrain", "task", "list", "--page", "0"])
    assert result == 1
    assert urlopen_called == []


def test_main_logout_bypasses_authentication(monkeypatch, sessions_creds_file, capsys):
    sessions_creds_file.write_text("not valid json")
    auth_checks = []
    monkeypatch.setattr(
        "cbrain_cli.main.is_authenticated",
        lambda: auth_checks.append(True) or True,
    )
    result = run_main(monkeypatch, ["cbrain", "logout"])
    assert result == 0
    assert auth_checks == []
    assert not sessions_creds_file.exists()


def test_config_import_does_not_create_home_dir(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    import cbrain_cli.config as config_mod

    importlib.reload(config_mod)
    assert not (home / ".config" / "cbrain").exists()


def test_main_version_does_not_create_config_dir(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    run_main(monkeypatch, ["cbrain", "version"])
    assert not (home / ".config").exists()


def test_main_task_list_bourreau_id_parses_and_dispatches(
    monkeypatch, fake_credentials, capture_urlopen
):
    patch_module_locals(monkeypatch, "cbrain_cli.data.tasks")
    configure, captured = capture_urlopen
    configure([])
    result = run_main(monkeypatch, ["cbrain", "task", "list", "bourreau-id", "7"])
    assert result is None
    assert "bourreau_id=7" in captured["url"]


def test_main_no_command_prints_help(capsys):
    from cbrain_cli.main import main

    assert main([]) is None
    assert "usage:" in capsys.readouterr().out.lower()


def test_main_missing_subcommand_action_returns_1(monkeypatch, fake_credentials, capsys):
    result = run_main(monkeypatch, ["cbrain", "file"])
    assert result == 1
