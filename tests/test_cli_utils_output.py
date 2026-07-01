import json
from unittest.mock import MagicMock

import pytest

from cbrain_cli.cli_utils import (
    display_key_value_table,
    dynamic_table_print,
    jsonl_printer,
    version_info,
)


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
    version_info(MagicMock())
    assert "cbrain cli client version" in capsys.readouterr().out
