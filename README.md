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
- [CBRAIN API Documentation (Swagger)](https://app.swaggerhub.com/apis/prioux/CBRAIN/7.0.0)

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
- `file (f)` - Manage individual file operations and metadata
- `background-activities` - Monitor and manage long-running background processes
- `data-providers` - Configure and manage data storage locations and access
- `files` - List, upload, download, and organize research data files
- `projects` - Create and manage research project workspaces
- `remote_resources` - Configure computational clusters and processing resources
- `tags` - Apply and manage metadata tags for organizing content
- `tasks` - Submit, show and manage computational analysis jobs
- `tool_configs` - Configure analysis tools and processing parameters
- `tools` - Browse available analysis tools and their capabilities

## Command Examples

<p align="center">
<img src=https://github.com/user-attachments/assets/ae3fe36d-a83d-4cbf-a245-c9242c60c9ff" alt="List, Total and Get GIF" width="500" height="300">
</p>

> <details><summary> Used in the above GIF</summary>
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
  <img src=https://github.com/user-attachments/assets/21ebd917-e84b-4616-bcfa-6c2802220efe " alt="List, Total and Get GIF" width="500" height="300">

> <details><summary> Used in the above GIF</summary>
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
