**A Google Summer of Code (GSoC) 2025 Project**

A command-line interface to a CBRAIN service
============================================

This repository contains a UNIX command-line interface (CLI) for [CBRAIN](https://github.com/aces/cbrain), a web-based neuroinformatics platform designed for collaborative brain imaging research. CBRAIN enables researchers to securely manage large neuroimaging datasets, share data across institutions, and execute neuroscience analysis pipelines on distributed high-performance computing (HPC) resources through a unified web and API-driven interface.


>The interface is implemented in Python using only standard libraries - no external dependencies required.


## CBRAIN Access Options

There are two main ways to access CBRAIN:

1. **McGill Production Portal** (Recommended for Regular Users)
   - Access the McGill-supported CBRAIN production portal at: https://portal.cbrain.mcgill.ca/
   - No local installation required
   - Web-based interface for most common operations

2. **Custom/Development Setup**
   - Deploy CBRAIN on your lab cluster, cloud, or virtual machine
   - Suitable for organizations that require their own CBRAIN instance or which prefer to host CBRAIN themselves due to legal or corporate requirements.
   - Local installation only needed for:
     - CLI software developers
     - Power users developing/debugging custom CLI scripts
   - Follow setup instructions at [CBRAIN GitHub Repository](https://github.com/aces/cbrain) if you need a local instance
## Project Context

This project is developed as part of **Google Summer of Code (GSoC) 2025**, under the mentorship of the CBRAIN development team and sponsored by INCF (International Neuroinformatics Coordinating Facility). The goal of this project is to provide a robust, dependency-free command-line interface to the CBRAIN platform, enabling scripting, automation, and power-user workflows.


## Installation

This CLI tool uses pure Python with no external library dependencies, making installation straightforward.

This design choice ensures maximum portability across HPC systems where installing third-party Python packages may not be possible.


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
- [CBRAIN API Documentation (Swagger)](https://app.swaggerhub.com/apis/prioux/CBRAIN/7.0.0)

## CLI Usage

The main command is called "cbrain" and as is typical for such clients, works
with a set of subcommand and options.

### Basic Usage

To use the CBRAIN CLI, you can execute variations of the following command in your terminal:

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
## Subcommands Overview

Each model supports standard REST-style actions such as `list`, `show`, `create`, `update`, and `delete` where applicable.

Examples:

```bash
# Project
cbrain project list
cbrain project show <id>
cbrain project switch <id>

# File
cbrain file list
cbrain file show <id>
cbrain file upload <local_path>

# Task
cbrain task list
cbrain task show <id>
cbrain task create <tool_config_id>
cbrain task list bourreau-id <id>

# Tool
cbrain tool list
cbrain tool show <id>

# Tool Configuration
cbrain tool-config list
cbrain tool-config show <id>
```


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

### Continuous Integration

Continuous Integration (CI) tests and framework were initially configured by P. Rioux, providing automated validation of the codebase. This infrastructure follows best open source practices and ensures code quality through automated testing.

## License

See [LICENSE](LICENSE) file for details.
