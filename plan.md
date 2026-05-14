# CBRAIN CLI Improvement Backlog

This is the full technical backlog. It is intentionally broader than one summer project.

For the student-facing 3-month scope, use `summer-student-scope.md`. That document explains which parts of this backlog are required, which are optional, and which are out of scope.

## Priority Model

- **Phase 1:** user-visible correctness bugs.
- **Phase 2:** low-hanging guardrails that make future work safer.
- **Phase 3:** output and UX consistency.
- **Phase 4:** incremental architecture cleanup.
- **Phase 5:** documentation and compatibility.

# Phase 1: Correctness Fixes

## 1. Fix `task list bourreau-id <id>` filtering

**Problem:** The parser accepts `bourreau-id`, but the data code checks `bourreau_id`, so the filter is ignored.

**Do:**
- Keep the public CLI spelling as `bourreau-id`.
- Use argparse `dest=` or normalization so internal code sees `bourreau_id`.
- Add coverage proving the generated request includes `bourreau_id=...`.

**Verify:** `cbrain task list bourreau-id 3` sends the expected filter.

## 2. Stop execution after invalid pagination

**Problem:** `pagination()` returns `None` for invalid input, but callers continue. Some crash; others make the wrong request.

**Do:**
- Give pagination a clear contract: raise a validation error or return a handled sentinel.
- Apply the same behavior to all paginated list commands.
- Ensure invalid pagination makes no network request.

**Verify:** `--per-page 1` and `--page 0` return a clear error and non-zero exit.

## 3. Fix `tool show <id>` lookup

**Problem:** `tool show` fetches only the first `/tools` page and filters client-side, so valid tools outside page 1 can appear missing.

**Do:**
- Prefer a direct `/tools/{id}` request if available.
- Otherwise fetch deliberately and document the limitation.
- Split `tool list` and `tool show` data functions.

**Verify:** A tool outside the first default page can be shown correctly.

## 4. Allow `logout` to clean up invalid credentials

**Problem:** `main()` blocks `logout` behind `is_authenticated()`, making cleanup unreachable for malformed credentials.

**Do:**
- Dispatch `logout` without requiring authentication.
- Make local credential removal robust when the file is missing or malformed.

**Verify:** A malformed credentials file is removed by `cbrain logout`.

## 5. Remove import-time config directory creation

**Problem:** `config.py` creates `~/.config/cbrain` at import time, so read-only commands can fail before parsing.

**Do:**
- Keep credential paths as constants.
- Create directories only when writing credentials.
- Ensure reads tolerate missing files/directories.

**Verify:** `cbrain --help` and `cbrain version` do not write to `HOME`.

## 6. Print empty list results consistently

**Problem:** Handlers using `if result:` suppress valid empty lists.

**Do:**
- Use `is not None` for list command results.
- Let formatters handle empty-list messages.
- Ensure JSON mode emits `[]`.

**Verify:** Empty API list responses produce useful normal output and valid JSON/JSONL behavior.

## 7. Implement or remove `project unswitch`

**Problem:** `project unswitch` is advertised but only prints a not-implemented message.

**Do:**
- Prefer implementing it by clearing `current_group_id` and `current_group_name`.
- Make it idempotent when no project is set.
- Respect `--json` and `--jsonl`.

**Verify:** `project switch`, `project unswitch`, and `project show` behave coherently.

# Phase 2: Low-Hanging Guardrails

## 8. Enforce Ruff linting and formatting

**Problem:** Ruff is configured but not clearly enforced as part of routine development.

**Do:**
- Standardize `ruff check .` and `ruff format .`.
- Add pre-commit and/or CI enforcement.
- Document the commands.

**Verify:** CI or local checks fail on lint/format drift.

## 9. Add unit tests beside capture tests

**Problem:** Capture tests protect output but do not isolate parsing, validation, request construction, or handler contracts.

**Do:**
- Add a minimal unit test harness, preferably `pytest`.
- Cover Phase 1 regressions first.
- Mock `urllib.request.urlopen` for request tests.

**Verify:** `python -m pytest` runs without a live CBRAIN server.

## 10. Add regression tests for falsey valid results

**Problem:** Empty lists and possibly empty dictionaries can be valid responses.

**Do:**
- Test empty list handling for each list handler.
- Decide explicitly whether empty dictionaries are valid for show commands.

**Verify:** Empty successful responses do not disappear.

## 11. Add HTTP timeouts

**Problem:** `urlopen()` calls have no timeout and can hang indefinitely.

**Do:**
- Add a default timeout, for example 30 seconds.
- Make timeout errors use shared error handling.
- Optionally allow environment or config override later.

**Verify:** Mocked timeout errors return clear messages and non-zero status.

## 12. Protect credentials file permissions

**Problem:** API tokens are stored as plain JSON without explicit permission handling.

**Do:**
- Create credential files with user-private permissions where supported.
- Preserve restrictive permissions when updating.
- Handle non-POSIX platforms gracefully.

**Verify:** On POSIX, credentials are written with private permissions.

## 13. Use one source of truth for versioning

**Problem:** `version_info()` hardcodes `1.0`, while repository tags may differ.

**Do:**
- Put version metadata in one place.
- Make `cbrain version` read package metadata when installed.
- Provide a source-tree fallback.

**Verify:** Reported version matches package metadata and release tags.

## 14. Add a contributor checklist

**Problem:** Review expectations are implicit.

**Do:**
- Add a short checklist to `README.md` or `CONTRIBUTING.md`.
- Include Ruff, tests, capture tests, output modes, data-layer printing, and credential safety.

**Verify:** Contributors can find the checklist before opening PRs.

## 15. Treat linting as a baseline

**Problem:** A clean Ruff run does not prove command behavior, output modes, or architecture are correct.

**Do:**
- Document that linting complements tests and review.
- Keep architecture-sensitive checks in the review checklist.

**Verify:** CI includes both lint/format checks and tests.

# Phase 3: Output and UX Consistency

## 16. Audit global `--json` and `--jsonl` behavior

**Problem:** Several commands ignore global output flags or always print JSON/plain text.

**Known examples:** `version`, `tool-config boutiques-descriptor`, `dataprovider is-alive`, `dataprovider delete-unregistered-files`, `project switch all`, file operations, and tag operations.

**Do:**
- Create a command/output matrix.
- Convert operation commands to structured result dictionaries.
- Route machine-readable output through `json_printer()` and `jsonl_printer()`.

**Verify:** Representative commands work in normal, JSON, and JSONL modes.

## 17. Make not-implemented behavior structured

**Problem:** Not-implemented paths print prose and return inconsistently.

**Known examples:** `project switch all`, `project unswitch`, `task operation`.

**Do:**
- Decide whether each command should exist.
- If it remains, return non-zero and emit structured JSON/JSONL errors.

**Verify:** Not-implemented commands behave consistently in all output modes.

## 18. Stabilize command vocabulary

**Problem:** Public terms and option names are inconsistent: `dataprovider`, `remote-resource`, `bourreau-id`, `dp-id`, `data-provider`, etc.

**Do:**
- Decide canonical public terms.
- Keep backward-compatible aliases where practical.
- Improve help text for CBRAIN-specific terms.

**Verify:** `cbrain --help` and subcommand help read consistently.

## 19. Clarify destructive command safety

**Problem:** Delete and cleanup commands need clear confirmation, force, partial success, and script behavior.

**Do:**
- Decide which destructive commands require confirmation.
- Add `--yes` or `--force` where appropriate.
- Return structured operation results for scripts.

**Verify:** Destructive commands behave predictably in interactive and non-interactive contexts.

## 20. Add coherent verbose/debug mode

**Problem:** Debug behavior is ad hoc and mostly tied to `whoami --version`.

**Do:**
- Add a global `--verbose` or `--debug`.
- Print sanitized method/path/status diagnostics.
- Never print raw tokens or passwords.

**Verify:** Debug output is useful and credential-safe.

# Phase 4: Incremental Architecture Cleanup

## 21. Define command return contracts

**Problem:** Functions return mixed values: `None`, `1`, lists, dicts, and tuples.

**Do:**
- Data functions return domain data or raise typed errors.
- Handlers orchestrate formatting and return exit codes.
- Formatters only print.
- Apply to one command family first.

**Verify:** Handler tests cover success, empty data, validation errors, and API errors.

## 22. Add typed CLI exceptions

**Problem:** Broad exception handling hides intent and makes failures inconsistent.

**Do:**
- Add exceptions such as `CliValidationError`, `CliApiError`, and `CliResponseError`.
- Update shared error handling to treat known errors clearly.

**Verify:** Expected failures get stable messages; unexpected failures still return non-zero.

## 23. Move printing out of data modules

**Problem:** Data modules mix API work, validation, and presentation by printing directly.

**Do:**
- Replace direct data-layer `print()` calls with typed errors or structured results.
- Keep user-facing output in handlers/formatters.

**Verify:** `cbrain_cli/data` has no new direct user-facing output.

## 24. Remove ad hoc background activity error handling

**Problem:** `list_background_activities()` catches all exceptions and bypasses shared error handling.

**Do:**
- Remove broad `except Exception`.
- Let shared handling process HTTP, URL, JSON, and unexpected errors.

**Verify:** Background activity failures match other command error styles.

## 25. Normalize CLI argument names before data-layer use

**Problem:** Raw public CLI spellings leak into data modules, causing bugs like `bourreau-id` vs `bourreau_id`.

**Do:**
- Use argparse `dest=` for normalized snake_case names.
- Translate API-specific field names at the API boundary.

**Verify:** Parsed args and generated API keys are both tested.

## 26. Split parser construction from execution

**Problem:** `main()` builds the parser and executes commands, making parser behavior harder to test.

**Do:**
- Extract `build_parser()`.
- Keep `main(argv=None)` for parse/auth/dispatch.

**Verify:** Parser tests can run without API calls.

## 27. Introduce a small CBRAIN API client

**Problem:** Data modules duplicate request creation, auth headers, JSON decoding, and error handling.

**Do:**
- Add a lightweight standard-library `CbrainClient`.
- Store base URL, token, user ID, and timeout on the client.
- Migrate one command family first.

**Verify:** Client tests mock `urlopen`; migrated commands still pass capture tests.

## 28. Centralize HTTP request construction

**Problem:** Request construction is duplicated and inconsistent.

**Do:**
- Centralize `get/post/put/delete`, URL joining, auth headers, JSON parsing, and HTTP error wrapping.
- If `CbrainClient` exists, put this logic there.

**Verify:** URL generation and JSON handling are unit tested.

## 29. Load authentication state at command execution time

**Problem:** Credentials are read into module globals at import time and can become stale.

**Do:**
- Add `load_credentials()`.
- Stop importing static `api_token`, `cbrain_url`, and `user_id` into data modules.
- Prefer passing credentials through the API client.

**Verify:** Login/logout/whoami behavior uses current credential state in one process.

# Phase 5: Documentation and Compatibility

## 30. Define supported CBRAIN API compatibility

**Problem:** Endpoint and response assumptions are spread across the codebase.

**Do:**
- Document the supported/tested CBRAIN API or server version.
- Centralize endpoint paths where practical.
- Add tests for representative response shapes.

**Verify:** README states the compatibility target.

## 31. Keep capture tests, but add faster isolated tests

**Problem:** Capture tests are valuable but fragile as the only safety net.

**Do:**
- Keep capture tests for end-to-end output.
- Use unit tests for parsing, validation, request construction, and formatter behavior.
- Run unit tests on every CI job.

**Verify:** Request bugs fail unit tests; output regressions fail capture tests.

## 32. Document internal boundaries

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
