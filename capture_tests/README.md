# CBRAIN CLI Capture Tests

Capture tests are end-to-end output regression tests for the `cbrain` command. They complement the unit suite: use unit tests for parsing, validation, request construction, client behavior, handler contracts, and formatters; use capture tests when live-server compatibility or user-visible terminal output matters.

This layer intentionally provides a strong but slower signal: CI provisions MariaDB, checks out and boots the CBRAIN Rails server, migrates and seeds its test database, runs the CLI transcript, and compares the result. The project plans to add faster subprocess-level tests with a fake HTTP server for most cross-layer behavior while retaining a focused set of these live-server checks. See `plan.md` item 30.

## How They Work

1. `cbrain_cli_commands` defines the commands to exercise.
2. `capture_wrapper` runs them and records exit codes, standard output, and standard error.
3. `run_and_diff_captures` normalizes variable timestamps and compares the result with `expected_captures.txt`.
4. A difference fails the test and produces `git_captures.diff`.

The GitHub Actions workflow in `.github/workflows/capture_tests.yaml` provisions a seeded CBRAIN test server, runs this workflow, and uploads the diff artifact when present. It checks out the current default branch of `aces/cbrain`, so a passing run is also the repository's live-server compatibility signal.

## Running Locally

Local capture tests require:

- a CBRAIN test server on `localhost:3000`;
- the expected test database seeds, including the API and Bourreau test data;
- a disposable CBRAIN CLI credential file for that test server.

From the repository root, run:

```bash
cd capture_tests
bash run_and_diff_captures
```

If output changed intentionally, review the generated diff carefully before updating `expected_captures.txt`. Do not update the fixture merely to make CI green.

Each command in `cbrain_cli_commands` should protect a specific compatibility contract or regression. Prefer a focused unit or lightweight integration test when a behavior does not require the live CBRAIN server or a golden terminal transcript.

## Credential Safety

`switch_session` writes test credentials directly to `$HOME/.config/cbrain/credentials.json`. Running it can overwrite a real local CLI session. Use an isolated home directory or back up your credentials, and never use production credentials in capture tests, fixtures, logs, or commits.

## Credits

Pierre Rioux <pierre.rioux@mcgill.ca>, July 2025
