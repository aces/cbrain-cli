# CBRAIN CLI Improvement Backlog

This is the full technical backlog. It is intentionally broader than one summer project.

For the student-facing 3-month scope, use `summer-student-scope.md`. That document explains which parts of this backlog are required, which are optional, and which are out of scope.

## Priority Model

- **Phase 1:** user-visible correctness bugs.
- **Phase 2:** low-hanging guardrails that make future work safer.
- **Phase 3:** output and UX consistency.
- **Phase 4:** incremental architecture cleanup.
- **Phase 5:** documentation and compatibility.

## Progress

- Phase 1 items 2-7 completed in PR #45.
- Phase 2 item 8 completed in PR #45.

# Phase 1: Correctness Fixes

## 1. Fix `task list bourreau-id <id>` filtering

**Problem:** The parser accepts `bourreau-id`, but the data code checks `bourreau_id`, so the filter is ignored.

**Do:**
- Keep the public CLI spelling as `bourreau-id`.
- Use argparse `dest=` or normalization so internal code sees `bourreau_id`.
- Add coverage proving the generated request includes `bourreau_id=...`.

**Verify:** `cbrain task list bourreau-id 3` sends the expected filter.

## 2. Stop execution after invalid pagination

**Status:** Completed in PR #45.

**Problem:** `pagination()` returns `None` for invalid input, but callers continue. Some crash; others make the wrong request.

**Do:**
- Give pagination a clear contract: raise a validation error or return a handled sentinel.
- Apply the same behavior to all paginated list commands.
- Ensure invalid pagination makes no network request.

**Verify:** `--per-page 1` and `--page 0` return a clear error and non-zero exit.

## 3. Fix `tool show <id>` lookup

**Status:** Completed in PR #45.

**Problem:** `tool show` fetches only the first `/tools` page and filters client-side, so valid tools outside page 1 can appear missing.

**Do:**
- Prefer a direct `/tools/{id}` request if available.
- Otherwise fetch deliberately and document the limitation.
- Split `tool list` and `tool show` data functions.

**Verify:** A tool outside the first default page can be shown correctly.

## 4. Allow `logout` to clean up invalid credentials

**Status:** Completed in PR #45.

**Problem:** `main()` blocks `logout` behind `is_authenticated()`, making cleanup unreachable for malformed credentials.

**Do:**
- Dispatch `logout` without requiring authentication.
- Make local credential removal robust when the file is missing or malformed.

**Verify:** A malformed credentials file is removed by `cbrain logout`.

## 5. Remove import-time config directory creation

**Status:** Completed in PR #45.

**Problem:** `config.py` creates `~/.config/cbrain` at import time, so read-only commands can fail before parsing.

**Do:**
- Keep credential paths as constants.
- Create directories only when writing credentials.
- Ensure reads tolerate missing files/directories.

**Verify:** `cbrain --help` and `cbrain version` do not write to `HOME`.

## 6. Print empty list results consistently

**Status:** Completed in PR #45.

**Problem:** Handlers using `if result:` suppress valid empty lists.

**Do:**
- Use `is not None` for list command results.
- Let formatters handle empty-list messages.
- Ensure JSON mode emits `[]`.

**Verify:** Empty API list responses produce useful normal output and valid JSON/JSONL behavior.

## 7. Implement or remove `project unswitch`

**Status:** Completed in PR #45.

**Problem:** `project unswitch` is advertised but only prints a not-implemented message.

**Do:**
- Prefer implementing it by clearing `current_group_id` and `current_group_name`.
- Make it idempotent when no project is set.
- Respect `--json` and `--jsonl`.

**Verify:** `project switch`, `project unswitch`, and `project show` behave coherently.

# Phase 2: Low-Hanging Guardrails

## 8. Add CI enforcement for Ruff linting and formatting

**Status:** Completed in PR #45.

**Problem:** Ruff is configured, pre-commit hooks exist, and README documents local lint/format commands. What is still missing is a CI check that fails when linting or formatting drifts.

**Do:**
- Add a GitHub Actions job for `ruff check .`.
- Add a GitHub Actions job or step for `ruff format --check .`.
- Keep the existing pre-commit and README workflow in sync with CI.

**Verify:** CI fails on a deliberately unformatted or lint-invalid change.

## 9. Add unit tests beside capture tests

**Problem:** Capture tests protect end-to-end CLI output, but they do not isolate parsing, validation, request construction, handler contracts, or falsey-but-valid responses.

**Do:**
- Add a minimal unit test harness, preferably `pytest`.
- Cover Phase 1 regressions first.
- Include regression tests for empty list responses and other falsey-but-valid results.
- Mock `urllib.request.urlopen` for request tests.
- Run unit tests in CI.

**Verify:** `python -m pytest` runs without a live CBRAIN server.

## 10. Add HTTP timeouts

**Problem:** `urlopen()` calls have no timeout and can hang indefinitely.

**Do:**
- Add a default timeout, for example 30 seconds.
- Make timeout errors use shared error handling.
- Optionally allow environment or config override later.

**Verify:** Mocked timeout errors return clear messages and non-zero status.

## 11. Protect credentials file permissions

**Problem:** API tokens are stored as plain JSON without explicit permission handling.

**Do:**
- Create credential files with user-private permissions where supported.
- Preserve restrictive permissions when updating.
- Handle non-POSIX platforms gracefully.

**Verify:** On POSIX, credentials are written with private permissions.

## 12. Use one source of truth for versioning

**Problem:** `version_info()` hardcodes `1.0`, while repository tags may differ.

**Do:**
- Put version metadata in one place.
- Make `cbrain version` read package metadata when installed.
- Provide a source-tree fallback.

**Verify:** Reported version matches package metadata and release tags.

## 13. Add general contributor checklist and quality-gate docs

**Problem:** README now documents local developer commands, and `summer-student-scope.md` has a student PR checklist, but the repository still lacks a general contributor checklist that applies to all PRs.

**Do:**
- Add a short checklist to `README.md` or `CONTRIBUTING.md`.
- Include Ruff, unit tests, capture tests, output modes, data-layer printing, credential safety, and public command compatibility.
- State explicitly that a clean Ruff run is necessary but not sufficient; behavior still needs tests and review.

**Verify:** Contributors can find the checklist before opening PRs.

# Phase 3: Output and UX Consistency

## 14. Audit global `--json` and `--jsonl` behavior

**Problem:** Several commands ignore global output flags or always print JSON/plain text.

**Known examples:** `version`, `tool-config boutiques-descriptor`, `dataprovider is-alive`, `dataprovider delete-unregistered-files`, `project switch all`, file operations, and tag operations.

**Do:**
- Create a command/output matrix.
- Convert operation commands to structured result dictionaries.
- Route machine-readable output through `json_printer()` and `jsonl_printer()`.

**Verify:** Representative commands work in normal, JSON, and JSONL modes.

## 15. Make not-implemented behavior structured

**Problem:** Not-implemented paths print prose and return inconsistently.

**Known examples:** `project switch all`, `project unswitch`, `task operation`.

**Do:**
- Decide whether each command should exist.
- If it remains, return non-zero and emit structured JSON/JSONL errors.

**Verify:** Not-implemented commands behave consistently in all output modes.

## 16. Stabilize command vocabulary

**Problem:** Public terms and option names are inconsistent: `dataprovider`, `remote-resource`, `bourreau-id`, `dp-id`, `data-provider`, etc.

**Do:**
- Decide canonical public terms.
- Keep backward-compatible aliases where practical.
- Improve help text for CBRAIN-specific terms.

**Verify:** `cbrain --help` and subcommand help read consistently.

## 17. Clarify destructive command safety

**Problem:** Delete and cleanup commands need clear confirmation, force, partial success, and script behavior.

**Do:**
- Decide which destructive commands require confirmation.
- Add `--yes` or `--force` where appropriate.
- Return structured operation results for scripts.

**Verify:** Destructive commands behave predictably in interactive and non-interactive contexts.

## 18. Add coherent verbose/debug mode

**Problem:** Debug behavior is ad hoc and mostly tied to `whoami --version`.

**Do:**
- Add a global `--verbose` or `--debug`.
- Print sanitized method/path/status diagnostics.
- Never print raw tokens or passwords.

**Verify:** Debug output is useful and credential-safe.

# Phase 4: Incremental Architecture Cleanup

## 19. Define command return contracts

**Problem:** Functions return mixed values: `None`, `1`, lists, dicts, and tuples.

**Do:**
- Data functions return domain data or raise typed errors.
- Handlers orchestrate formatting and return exit codes.
- Formatters only print.
- Apply to one command family first.

**Verify:** Handler tests cover success, empty data, validation errors, and API errors.

## 20. Add typed CLI exceptions

**Problem:** Broad exception handling hides intent and makes failures inconsistent.

**Do:**
- Add exceptions such as `CliValidationError`, `CliApiError`, and `CliResponseError`.
- Update shared error handling to treat known errors clearly.

**Verify:** Expected failures get stable messages; unexpected failures still return non-zero.

## 21. Move printing out of data modules

**Problem:** Data modules mix API work, validation, and presentation by printing directly.

**Do:**
- Replace direct data-layer `print()` calls with typed errors or structured results.
- Keep user-facing output in handlers/formatters.

**Verify:** `cbrain_cli/data` has no new direct user-facing output.

## 22. Remove ad hoc background activity error handling

**Problem:** `list_background_activities()` catches all exceptions and bypasses shared error handling.

**Do:**
- Remove broad `except Exception`.
- Let shared handling process HTTP, URL, JSON, and unexpected errors.

**Verify:** Background activity failures match other command error styles.

## 23. Normalize CLI argument names before data-layer use

**Problem:** Raw public CLI spellings leak into data modules, causing bugs like `bourreau-id` vs `bourreau_id`.

**Do:**
- Use argparse `dest=` for normalized snake_case names.
- Translate API-specific field names at the API boundary.

**Verify:** Parsed args and generated API keys are both tested.

## 24. Split parser construction from execution

**Problem:** `main()` builds the parser and executes commands, making parser behavior harder to test.

**Do:**
- Extract `build_parser()`.
- Keep `main(argv=None)` for parse/auth/dispatch.

**Verify:** Parser tests can run without API calls.

## 25. Introduce a small CBRAIN API client and centralize request handling

**Problem:** Data modules duplicate request creation, auth headers, URL joining, JSON decoding, timeouts, and error handling.

**Do:**
- Add a lightweight standard-library `CbrainClient`.
- Store base URL, token, user ID, and timeout on the client.
- Centralize `get/post/put/delete`, auth headers, URL joining, JSON parsing, and HTTP error wrapping in the client.
- Migrate one command family first.

**Verify:** Client tests mock `urlopen`; URL generation and JSON handling are unit tested; migrated commands still pass capture tests.

## 26. Load authentication state at command execution time

**Problem:** Credentials are read into module globals at import time and can become stale.

**Do:**
- Add `load_credentials()`.
- Stop importing static `api_token`, `cbrain_url`, and `user_id` into data modules.
- Prefer passing credentials through the API client.

**Verify:** Login/logout/whoami behavior uses current credential state in one process.

# Phase 5: Documentation and Compatibility

## 27. Define supported CBRAIN API compatibility

**Problem:** README links to CBRAIN/API references, but it does not state which CBRAIN server or API version this CLI is tested against.

**Do:**
- Document the supported/tested CBRAIN API or server version.
- Centralize endpoint paths where practical.
- Add tests for representative response shapes.

**Verify:** README states the compatibility target.

## 28. Document test strategy

**Problem:** README explains capture tests, but the overall testing strategy should distinguish what belongs in capture tests versus unit tests once unit tests exist.

**Do:**
- Document that capture tests are for end-to-end output regression.
- Document that unit tests are for parsing, validation, request construction, handler contracts, and formatter behavior.
- Link the test commands once unit tests are added.

**Verify:** Contributors know which test type to update for a given change.

## 29. Document internal boundaries

**Problem:** The intended layering is implicit.

**Do:**
- Add a short architecture section:
  - `main.py`: parser and dispatch.
  - `handlers.py`: orchestration and exit codes.
  - `data/`: API calls and domain data.
  - `formatter/`: user-facing output.
  - `cli_utils.py` or `api.py`: shared helpers and errors.
- State that data modules should not print.

**Verify:** Contributor docs match the architecture used by migrated command families.
