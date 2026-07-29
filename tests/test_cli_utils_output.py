import configparser
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cbrain_cli.cli_utils import (
    CliValidationError,
    confirm_destructive,
    display_key_value_table,
    dynamic_table_print,
    jsonl_printer,
    version_info,
)


def _setup_cfg_version():
    cfg = configparser.ConfigParser()
    cfg.read(Path(__file__).resolve().parents[1] / "setup.cfg")
    return cfg["metadata"]["version"]


def test_jsonl_printer_list(capsys):
    jsonl_printer([{"a": 1}, {"b": 2}])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1}


def test_jsonl_printer_dict(capsys):
    jsonl_printer({"ok": True})
    assert json.loads(capsys.readouterr().out.strip()) == {"ok": True}


def test_display_key_value_table(capsys):
    display_key_value_table([("Name", "Alpha"), ("ID", "1")])
    out = capsys.readouterr().out
    assert "Name" in out
    assert "Alpha" in out


def test_dynamic_table_print_empty(capsys):
    dynamic_table_print([], ["id"], ["ID"])
    assert "No data found." in capsys.readouterr().out


def test_dynamic_table_print_with_rows(capsys):
    dynamic_table_print(
        [{"id": 1, "description": "short"}],
        ["id", "description"],
        ["ID", "Description"],
        wrap_columns=["description"],
        max_row_lines=2,
    )
    out = capsys.readouterr().out
    assert "ID" in out
    assert "short" in out


def test_dynamic_table_print_header_mismatch_raises():
    with pytest.raises(ValueError):
        dynamic_table_print([{"id": 1}], ["id"], ["ID", "Extra"])


def test_version_info(capsys):
    import importlib.metadata

    try:
        expected = importlib.metadata.version("cbrain-cli")
    except importlib.metadata.PackageNotFoundError:
        expected = _setup_cfg_version()
    assert version_info(MagicMock(json=False, jsonl=False)) == 0
    assert f"cbrain cli client version {expected}" in capsys.readouterr().out


def test_version_info_prefers_package_metadata(monkeypatch, capsys):
    monkeypatch.setattr("importlib.metadata.version", lambda _name: "9.9.9-installed")
    assert version_info(MagicMock(json=False, jsonl=False)) == 0
    assert "cbrain cli client version 9.9.9-installed" in capsys.readouterr().out


def test_version_info_falls_back_to_setup_cfg(monkeypatch, capsys):
    import importlib.metadata

    def boom(_name):
        raise importlib.metadata.PackageNotFoundError("cbrain-cli")

    monkeypatch.setattr(importlib.metadata, "version", boom)
    assert version_info(MagicMock(json=False, jsonl=False)) == 0
    assert f"cbrain cli client version {_setup_cfg_version()}" in capsys.readouterr().out


def test_version_info_json(capsys):
    version_info(MagicMock(json=True, jsonl=False))
    out = json.loads(capsys.readouterr().out)
    assert "version" in out


def test_version_info_jsonl(capsys):
    version_info(MagicMock(json=False, jsonl=True))
    out = json.loads(capsys.readouterr().out.strip())
    assert "version" in out


def test_confirm_destructive_yes_flag():
    assert confirm_destructive(MagicMock(yes=True), "Delete?") is True


def test_confirm_destructive_noninteractive_requires_yes(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(CliValidationError, match="--yes"):
        confirm_destructive(MagicMock(yes=False, json=False, jsonl=False), "Delete?")


def test_confirm_destructive_json_requires_yes(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with pytest.raises(CliValidationError, match="--yes"):
        confirm_destructive(MagicMock(yes=False, json=True, jsonl=False), "Delete?")


def test_confirm_destructive_tty_accepts_y(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert confirm_destructive(MagicMock(yes=False, json=False, jsonl=False), "Delete?") is True


def test_confirm_destructive_tty_declines(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert confirm_destructive(MagicMock(yes=False, json=False, jsonl=False), "Delete?") is False
    assert "Aborted." in capsys.readouterr().out


def test_confirm_destructive_tty_eof(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    def boom(_):
        raise EOFError

    monkeypatch.setattr("builtins.input", boom)
    assert confirm_destructive(MagicMock(yes=False, json=False, jsonl=False), "Delete?") is False
    assert "Aborted." in capsys.readouterr().out
