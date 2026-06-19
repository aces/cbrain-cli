<!---
Thank you for your pull request! 🚀

CI runs pre-commit (Ruff, formatting, hooks) and capture tests on every pull request.
-->

### Contributor checklist

<!-- Please replace the empty checkboxes [ ] below with checked ones [x] accordingly. -->

- [ ] This pull request is on a [separate branch](https://docs.github.com/en/get-started/quickstart/github-flow) and not the main branch
- [ ] I ran `pre-commit run --all-files` and/or `pytest` as appropriate (see [Tests](https://github.com/aces/cbrain-cli/blob/main/README.md#tests) in the README)
- [ ] If CLI output changed intentionally, I updated `capture_tests/expected_captures.txt`
- [ ] No credentials, tokens, or session data appear in code, fixtures, logs, or this PR description

---

### Type of change

- [ ] Bug fix
- [ ] New feature or command behavior
- [ ] Documentation
- [ ] Tests only
- [ ] Other (describe below)

---

### Description

<!--
Summarize what this pull request changes and why. For multiple commits, a short overview helps reviewers.

Also consider including:
- User-visible behavior before and after (or "no user-visible change")
- Main files changed and what was done in them
- Whether `capture_tests/expected_captures.txt` was updated for intentional CLI output changes
- Screenshots or a short video, if helpful
-->

---

### Test plan

<!--
List the commands you ran and what they showed, for example:

- `pre-commit run --all-files`
- `pytest`
- `ruff check .`
- Capture tests (if applicable; see capture_tests/README.md)

If you did not run something, say why (e.g. no local CBRAIN server for capture tests).
-->

---

### Related issue

<!-- Link the issue below. Use "Closes #123" to close on merge, or write "No related issue." -->

- Closes #ISSUE_NUMBER
