# CBRAIN CLI

A command-line interface to a CBRAIN service
============================================

This repository contains a UNIX command-line interface (CLI) for [CBRAIN](https://github.com/aces/cbrain), a web-based neuroinformatics platform designed for collaborative brain imaging research. CBRAIN provides researchers with distributed computational resources, data management capabilities, and a framework for running neuroscience analysis pipelines across multiple high-performance computing environments.

>The interface is implemented in Python using only standard libraries - no external dependencies required.


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

When prompted for "Enter CBRAIN server URL prefix", enter:
- For McGill Production Portal: `https://portal.cbrain.mcgill.ca`
- For custom setup: Your CBRAIN instance URL

## API Reference

This CLI interfaces with the CBRAIN REST API. For complete API documentation and specifications, refer to:
- [CBRAIN API Documentation (Swagger)](https://portal.cbrain.mcgill.ca/swagger)

## CLI Usage

The main command is called "cbrain" and as is typical for such clients, works
with a set of subcommand and options.

### Basic Usage

To utilize the Cbrain cli, you can execute variations of the following command in your terminal:

```
cbrain -h     # view the cli options
cbrain [options] <MODEL> <ACTION> [id_or_args]
```
**Output Formats:**
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

The existing test suite is based on capture tests in `capture_tests/`. These are shell-based CLI output regression tests: they run commands from `capture_tests/cbrain_cli_commands` and compare the captured terminal output against `capture_tests/expected_captures.txt`.

Capture tests require a local CBRAIN test server on `localhost:3000` with the expected test database seed. The GitHub Actions workflow sets this up by checking out the CBRAIN server repository at https://github.com/aces/cbrain.

Focused unit tests should use `pytest` and should not require a live CBRAIN server:

```bash
pytest
```

When command output intentionally changes, update `capture_tests/expected_captures.txt`. When behavior changes without intended output changes, prefer adding focused unit tests where possible.

### Continuous Integration

Continuous Integration (CI) tests and framework were initially configured by P. Rioux, providing automated validation of the codebase. This infrastructure follows best open source practices and ensures code quality through automated testing.

## License

See [LICENSE](LICENSE) file for details.
