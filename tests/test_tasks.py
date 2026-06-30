import pytest

from cbrain_cli.cli_utils import CliValidationError
from cbrain_cli.data.tasks import list_tasks, show_task
from tests.conftest import make_args
from tests.conftest import patch_module_locals


@pytest.fixture(autouse=True)
def _patch_tasks_locals(monkeypatch):
    patch_module_locals(monkeypatch, "cbrain_cli.data.tasks")


def make_task_args(**kwargs):
    kwargs.setdefault("filter_name", None)
    kwargs.setdefault("bourreau_id", None)
    return make_args(**kwargs)


@pytest.mark.parametrize(
    "filter_name,bourreau_id,raises",
    [
        (None, None, False),
        ("bourreau-id", 7, False),
        ("bourreau-id", None, True),
        (None, 7, True),
    ],
)
def test_list_tasks_filter_validation(filter_name, bourreau_id, raises, mock_urlopen):
    if not raises:
        mock_urlopen([{"id": 1}])
    args = make_task_args(filter_name=filter_name, bourreau_id=bourreau_id)
    if raises:
        with pytest.raises(CliValidationError):
            list_tasks(args)
    else:
        result = list_tasks(args)
        assert isinstance(result, list)


def test_list_tasks_empty_list_is_not_error(mock_urlopen):
    """Empty list response must not raise — empty-list regression."""
    mock_urlopen([])
    assert list_tasks(make_task_args()) == []


def test_show_task_missing_id_raises():
    with pytest.raises(CliValidationError):
        show_task(make_task_args(task=None))


def test_show_task_returns_dict(mock_urlopen):
    mock_urlopen({"id": 2, "type": "CbrainTask::Diagnostics"})
    result = show_task(make_task_args(task=2))
    assert result["id"] == 2


def test_list_tasks_sends_bourreau_id_query(capture_urlopen):
    configure, captured = capture_urlopen
    configure([])
    list_tasks(make_task_args(filter_name="bourreau-id", bourreau_id=7))
    assert "bourreau_id=7" in captured["url"]


def test_list_tasks_unsupported_filter_raises():
    with pytest.raises(CliValidationError):
        list_tasks(make_task_args(filter_name="other", bourreau_id=1))


def test_operation_task_prints_json(monkeypatch, capsys):
    monkeypatch.setattr(
        "cbrain_cli.data.tasks.api_send",
        lambda *_, **__: ({"status": "ok"}, 200),
    )
    from cbrain_cli.data.tasks import operation_task

    operation_task(make_task_args())
    assert '"status": "ok"' in capsys.readouterr().out
