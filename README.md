# CBRAIN CLI

Command-line access to a CBRAIN service.

This repository contains a UNIX command-line interface (CLI) for [CBRAIN](https://github.com/aces/cbrain), a web-based neuroinformatics platform designed for collaborative brain imaging research. CBRAIN provides researchers with distributed computational resources, data management capabilities, and a framework for running neuroscience analysis pipelines across multiple high-performance computing environments.

> The runtime uses only the Python standard library; no third-party runtime dependencies are required.


## CBRAIN Access Options

There are two main ways to access CBRAIN:

1. **McGill Production Portal** (Recommended for Regular Users)
   - Access the McGill-supported CBRAIN production portal at: https://portal.cbrain.mcgill.ca/
   - No local installation required
   - Web-based interface for most common operations

2. **Custom/Development Setup**
   - Deploy CBRAIN on your lab cluster, cloud, or virtual machine
   - Suitable for organizations that require their own CBRAIN instance or which prefer to host CBRAIN themselves due to legal or corporate requirements
   - Local installation only needed for:
     - CLI software developers
     - Power users developing/debugging custom CLI scripts
   - Follow setup instructions at [CBRAIN GitHub Repository](https://github.com/aces/cbrain) if you need a local instance

## Installation

This CLI tool uses pure Python with no external library dependencies, making installation straightforward.

### Option 1: Direct Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/aces/cbrain-cli.git
   cd cbrain-cli
   ```

2. Run directly:
   ```bash
   ./cbrain --help # Make the cbrain script executable by `chmod +x cbrain`
   ```

### Option 2: Virtual Environment

For isolated usage:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Initial Setup

After installation, you need to login to your CBRAIN instance:

```bash
cbrain login
```

When prompted for the CBRAIN server base URL, enter:
- For McGill Production Portal: `https://portal.cbrain.mcgill.ca`
- For custom setup: Your CBRAIN instance URL

## API Reference

This CLI interfaces with the CBRAIN REST API. For complete API documentation and specifications, refer to:
- [CBRAIN API Documentation (Swagger)](https://portal.cbrain.mcgill.ca/swagger)

### Compatibility Target

The CLI does not currently claim compatibility with a numbered CBRAIN API release. Its end-to-end capture-test workflow checks the CLI against the current default branch of the [CBRAIN server repository](https://github.com/aces/cbrain), using that repository's seeded test database. Because the server checkout is not pinned, a passing capture-test run is the authoritative compatibility signal for the exact CLI commit being tested.

The unit suite separately checks request construction and representative response handling without requiring a live server.

## CLI Usage

The main command is called "cbrain" and as is typical for such clients, works
with a set of subcommand and options.

### Basic Usage

Use the following command pattern:

```text
cbrain -h     # view the cli options
cbrain [options] <MODEL> <ACTION> [id_or_args]
```

**Output formats:**

- `--json` or `-j`: JSON format output
- `--jsonl` or `-jl`: JSON Lines format (one JSON object per line)

## Available Commands

- `version`      - Show CLI version
- `login`        - Login to CBRAIN
- `logout`       - Logout from CBRAIN
- `whoami`       - Show current session
- `file`         - File operations
- `dataprovider` - Data provider operations
- `project`      - Project operations
- `tool`         - Tool operations
- `tool-config`  - Tool configuration operations
- `tag`          - Tag operations
- `background`   - Background activity operations
- `task`         - Task operations
- `remote-resource` - Remote resource operations

## Command Examples

<p align="center">
<img src="https://github.com/user-attachments/assets/ae3fe36d-a83d-4cbf-a245-c9242c60c9ff" alt="List, Total and Get GIF" width="500" height="300">
</p>

> <details><summary> Used cmds in the above GIF</summary>
>
> - `./cbrain project switch 2`
> - `./cbrain project show`
> - `./cbrain tool show 2`
>  - `./cbrain dataprovider show 4`
> - `./cbrain file show 4`
> - `./cbrain background show 15`
> - `./cbrain remote-resource show 2`
> - `./cbrain tag show 17`
> - `./cbrain task show 1`
>
> </details>

<p align="center">
  <img src="https://github.com/user-attachments/assets/21ebd917-e84b-4616-bcfa-6c2802220efe" alt="List, Total and Get GIF" width="500" height="300">
</p>

> <details><summary> Used cmds in the above GIF</summary>
>
> - `./cbrain file list`
> - `./cbrain project list`
> - `./cbrain background list`
>  - `./cbrain dataprovider list`
> - `./cbrain remote-resource list`
> - `./cbrain tag list`
> - `./cbrain task list`
> - `./cbrain task list bourreau-id 3`
>
> </details>

## Development

This is part of [**a GSoC (Google Summer of Code) 2025** project](https://summerofcode.withgoogle.com/programs/2025/projects/1An4Dp8N) sponsored by [INCF](https://www.incf.org/).

The lead developer is [axif0](https://github.com/axif0), mentored by the developers of the CBRAIN project.

Development continues as part of [**a GSoC (Google Summer of Code) 2026** project](https://summerofcode.withgoogle.com/programs/2026/projects/iJ7MpwX1), with [Rafsan Neloy](https://github.com/RafsanNeloy) contributing under the mentorship of the CBRAIN project developers.

### Developer Setup

Install the CLI in editable mode with the development tools:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

This project is a pure Python CLI. There is no separate compile or build step for normal development; installing in editable mode is enough to run the local `cbrain` command.

The `dev` extra installs the local review tools used by this repository:

- `ruff` for linting and formatting;
- `pytest` for focused unit tests;
- `pre-commit` for local hook checks.

### Linting And Formatting

Ruff is used for linting and formatting:

```bash
ruff check .
ruff format .
```

To check formatting without changing files:

```bash
ruff format --check .
```

### Pre-Commit Hooks

The repository includes a `.pre-commit-config.yaml`. Install the hooks with:

```bash
pre-commit install
```

The hooks currently:

- trim trailing whitespace;
- ensure files end with a newline;
- check YAML syntax;
- check Markdown links;
- run `ruff --fix`;
- run `ruff format`.

The generated capture fixture `capture_tests/expected_captures.txt` is excluded from whitespace hooks and from Ruff (via `pyproject.toml`) because exact captured output is intentional there.

To run the hooks manually:

```bash
pre-commit run --all-files
```

### Tests

The repository uses two complementary test layers:

- **Unit tests** cover parsing, validation, request construction, `CbrainClient`, handler contracts, formatters, exit codes, and regressions that do not require a live CBRAIN server.
- **Capture tests** cover end-to-end command behavior and terminal output against a seeded CBRAIN test server. They run commands from `capture_tests/cbrain_cli_commands` and compare the output with `capture_tests/expected_captures.txt`.

Run the unit suite with:

```bash
pytest
```

Capture tests require a local CBRAIN test server on `localhost:3000` with the expected test database seed. The GitHub Actions workflow sets this up by checking out the CBRAIN server repository at https://github.com/aces/cbrain.

Use unit tests for behavior and request-level changes. Update `capture_tests/expected_captures.txt` only when user-visible CLI output intentionally changes. See [capture_tests/README.md](capture_tests/README.md) for the capture workflow and its credential-safety warning.

### Architecture

The CLI follows these internal boundaries:

- `cbrain_cli/main.py` builds the parser, validates global concerns, and dispatches commands.
- `cbrain_cli/handlers.py` orchestrates data calls and formatting and defines command exit behavior.
- `cbrain_cli/data/` validates command-specific input and returns domain data; data modules must not print user-visible output.
- `cbrain_cli/formatter/` owns human-readable and machine-readable presentation.
- `cbrain_cli/cli_utils.py` contains `CbrainClient`, shared exceptions, error handling, pagination, and output helpers.
- `cbrain_cli/config.py` owns credential paths, persistence, headers, and runtime configuration defaults.

`CbrainClient.from_credentials()` loads authentication state when a command executes, avoiding stale import-time credentials. New API operations should use the client rather than constructing `urllib` requests in data modules.

### Contributor Checklist

Before opening a pull request:

- run `ruff check .` and `ruff format --check .`;
- run `pytest`;
- run capture tests when CLI output or live-server behavior may have changed, or state why they were not run;
- test normal, `--json`, and `--jsonl` output when command behavior changes;
- add focused regression coverage for behavior changes;
- keep user-visible printing out of data modules;
- preserve public commands, flags, and defaults unless a breaking change is explicitly agreed;
- confirm no credentials, tokens, passwords, or session data appear in code, fixtures, logs, or the PR description.

A clean lint and formatting run is necessary, but it does not replace behavioral tests and review.

### Continuous Integration

Continuous Integration (CI) tests and framework were initially configured by P. Rioux, providing automated validation of the codebase. This infrastructure follows best open source practices and ensures code quality through automated testing.

## License

See [LICENSE](LICENSE) file for details.
