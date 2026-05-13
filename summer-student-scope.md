# Summer Student Project Scope

This is the 3-month project brief. The detailed technical backlog is in `plan.md`; use this document to understand what is in scope for the summer and how to prioritize it.

The goal is not to rewrite the CLI. The goal is to fix the highest-impact correctness issues, add development guardrails, and establish one clean pattern that future contributors can continue.

## Project Goal

Improve CBRAIN CLI reliability and maintainability by:

- fixing the correctness bugs in Phase 1 of `plan.md`;
- adding tests, linting, formatting, and CI/pre-commit guardrails from Phase 2;
- improving output consistency for a selected command slice from Phase 3;
- starting, but not completing, the architecture cleanup in Phase 4;
- documenting what changed and what remains.

Success means reviewed, tested, merged improvements. It does not mean touching every module.

## Scope By Phase

### Phase 1: Required

Complete all Phase 1 items in `plan.md`. These are correctness fixes and should be treated as the baseline deliverable.

### Phase 2: Mostly Required

Complete the high-value guardrails from Phase 2 of `plan.md`: Ruff, tests, CI/pre-commit where practical, timeouts, credential permissions, versioning, and contributor checklist updates.

### Phase 3: Selected Slice

Do not try to make every command perfect. Pick a representative subset, preferably `project` and `task`, and make normal, JSON, and JSONL behavior consistent for that slice.

Avoid broad public command renaming during the summer unless explicitly agreed.

### Phase 4: Pattern Only

Start Phase 4 by establishing a pattern, not by migrating the whole codebase.

Recommended target:

- define return contracts;
- add typed CLI exceptions;
- introduce a small `CbrainClient` or shared API helper;
- migrate one command family, preferably `task` or `project`.

### Phase 5: Lightweight

Document the architecture boundaries, test workflow, Ruff workflow, supported/tested CBRAIN API version if known, and remaining follow-up work.

## Out Of Scope

Do not attempt these unless the required work is already complete and reviewed:

- migrating every command to `CbrainClient`;
- rewriting all return contracts across the whole CLI;
- making every command fully output-consistent;
- redesigning all destructive command safety behavior;
- broadly renaming public commands or options;
- replacing the capture test framework;
- adding external runtime dependencies beyond approved development tooling.

## Suggested Timeline

Note: in this repository, "capture tests" means the existing shell-based CLI output regression tests in `capture_tests/`. They run CLI commands and compare captured terminal output against `expected_captures.txt`.

### Month 1: Correctness

- Complete Phase 1.
- Add unit tests for those fixes.
- Keep capture tests passing.
- Start Ruff and CI/pre-commit work.

### Month 2: Guardrails And Output

- Complete most Phase 2 guardrails.
- Improve JSON/JSONL behavior for the selected command slice.
- Add regression tests for those output modes.
- Update contributor docs.

### Month 3: Architecture Pattern

- Introduce typed errors and/or a small API client.
- Migrate one command family to the new pattern.
- Add tests for the new pattern.
- Document the remaining backlog against `plan.md`.

## Expectations For You

- Work from your own fork of the repository.
- Open PRs from your fork to the upstream repository for review.
- Do not rewrite the CLI.
- Fix correctness first, then add guardrails, then improve one architecture slice.
- Keep PRs small enough to review.
- Add tests for every behavior change.
- Preserve public command behavior unless a change is explicitly agreed.
- Do not change public command names without discussion.
- Do not add new direct `print()` calls in data modules.
- Keep tokens and credentials out of logs, fixtures, and PR descriptions.
- When in doubt, preserve existing behavior and document follow-up work.

## PR Checklist

Each PR should answer:

- Is this PR opened from your fork against the upstream repository?
- What user-visible behavior changed?
- What tests were added or updated?
- Do `ruff check .` and `ruff format --check .` pass?
- Were capture tests affected?
- Does JSON/JSONL behavior still make sense?
- Did any data module gain direct output behavior?
- Are credentials and tokens protected?

## Definition Of Done

The summer project is successful if:

- all Phase 1 items in `plan.md` are fixed and tested;
- the project has regular lint/format/test guardrails;
- the selected command slice has consistent output behavior;
- one command family demonstrates the new architecture pattern;
- documentation explains what was done and what remains.
