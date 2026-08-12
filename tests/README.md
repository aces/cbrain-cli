# CBRAIN CLI Unit Tests

This directory contains the unit test suite for the CBRAIN CLI.

Where tests touch the network, the HTTP layer (`urllib.request.urlopen`) is
mocked, so **no real CBRAIN server is required**. Many tests exercise
parsers, formatters, config, or dispatch and do not use HTTP at all. For
live-server end-to-end output checks, see
[capture_tests/README.md](../capture_tests/README.md). Those capture tests
expect a seeded CBRAIN test instance; server setup follows the same pattern as
CBRAIN's own [API testing frameworks](https://github.com/aces/cbrain/blob/master/BrainPortal/test_api/README.md).

Alongside the test modules, __conftest.py__ provides shared helpers and pytest
fixtures used across the suite.

## Running the tests

From the repository root (with the `dev` extra installed):

```bash
pytest
```

With a coverage report:

```bash
pytest --cov=cbrain_cli
```

Selecting a subset by path or by test name substring:

```bash
pytest tests/test_files.py
pytest tests/test_sessions.py -k login
pytest tests -k "handler and not ops"
```

More options are available via `pytest --help`.

## Shared helpers and fixtures

__conftest.py__ is the common entry point for test scaffolding.

Helper functions:

- `make_args(**kwargs)` — fake `argparse.Namespace` (defaults: `page=1`, `per_page=25`)
- `parse_json_output(capsys)` — parse captured stdout as JSON
- `run_main(monkeypatch, argv)` — run `main()` with a fake `sys.argv`
- `install_auth()` — write known credentials so `CbrainClient.from_credentials()` succeeds
- `write_auth_credentials(path, ...)` — write a credentials JSON file to a given path
- `sample_credentials(**overrides)` — credentials dict with sensible defaults

Fixtures:

- `_isolate_credentials` (autouse) — redirect the credentials file to a temp directory so the real `~/.config/cbrain` file is never touched
- `creds_file` / `sessions_creds_file` — path to the isolated credentials file
- `fake_credentials` — known credentials for `is_authenticated()` and `CbrainClient`
- `mock_urlopen` — patch `urlopen` with one configurable response: `mock_urlopen(response_json, status=200)`
- `capture_urlopen` — like `mock_urlopen`, but also records URL, headers, method, and body; returns `(configure, captured)`

**Note:** credential isolation is automatic. Unit tests must not depend on a real login session.

## Test modules

### Data layer

- `test_background_activities.py` — list, show, empty list, missing ID
- `test_data_providers.py` — list, show (ID fallback), `is-alive`, `delete-unregistered-files`
- `test_files.py` — list (filters), show, upload, copy, move, delete, missing-arg validation
- `test_projects.py` — list, show, switch, unswitch, stale group cleanup
- `test_remote_resources.py` — list, show, empty list, missing ID
- `test_tags.py` — list, show, create, update, delete, missing-arg validation
- `test_tasks.py` — list (`bourreau-id` filter), show, operation
- `test_tool_configs.py` — list, show, Boutiques descriptor, missing ID
- `test_tools.py` — list (pagination), show (multi-page search, not-found)

### Formatter layer

- `test_formatters.py` — all `_fmt.py` outputs: normal, empty, `--json`, `--jsonl`

### Handlers

- `test_handlers.py` — list/show/switch/unswitch/`whoami` handler contracts; task operation success/empty/validation/API
- `test_handlers_ops.py` — dataprovider ops, file upload/copy/delete (incl. abort without `--yes`), tags, Boutiques

### Infrastructure

- `test_cbrain_client.py` — URL normalization, timeouts, GET/POST/DELETE, query params, multipart, HTTP errors
- `test_cli_utils_output.py` — tables, JSONL, `version_info`, `confirm_destructive`
- `test_config.py` — credential load/save, permissions, corrupt JSON
- `test_exit_codes.py` — mapped exit codes for HTTP, URL, validation, interrupt, unexpected errors
- `test_sessions.py` — login/logout edge cases and file cleanup
- `test_users.py` — `user_details` / `whoami`, including login-then-whoami flow

### Parsing and dispatch

- `test_parser.py` — command registration, kebab→snake flags, `--json` / `--jsonl`, pagination flags
- `test_main_dispatch.py` — auth bypass for logout/version, help paths, `task list bourreau-id`
- `test_pagination.py` — page / per-page bounds and query-param injection
