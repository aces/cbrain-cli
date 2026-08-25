import pytest

from cbrain_cli.cli_utils import CliValidationError, pagination
from tests.conftest import make_args


@pytest.mark.parametrize(
    "per_page,valid",
    [(4, False), (5, True), (25, True), (1000, True), (1001, False)],
)
def test_per_page_boundary(per_page, valid):
    args = make_args(per_page=per_page)
    if valid:
        result = pagination(args, {})
        assert result["per_page"] == str(per_page)
    else:
        with pytest.raises(CliValidationError) as exc_info:
            pagination(args, {})
        assert exc_info.value.field == "--per-page"


@pytest.mark.parametrize("page,valid", [(0, False), (1, True), (10, True)])
def test_page_boundary(page, valid):
    args = make_args(page=page)
    if valid:
        result = pagination(args, {})
        assert result["page"] == str(page)
    else:
        with pytest.raises(CliValidationError) as exc_info:
            pagination(args, {})
        assert exc_info.value.field == "--page"


def test_pagination_adds_both_keys_to_query_params():
    params = {"existing": "value"}
    result = pagination(make_args(page=2, per_page=50), params)
    assert result["page"] == "2"
    assert result["per_page"] == "50"
    assert result["existing"] == "value"


def test_pagination_returns_query_params():
    """Return value is the same dict that was mutated."""
    params = {}
    result = pagination(make_args(), params)
    assert result is params
