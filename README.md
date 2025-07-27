# CBRAIN CLI

A command-line interface to a CBRAIN service
============================================

This repository contains a UNIX command-line interface (CLI) for [CBRAIN](https://github.com/aces/cbrain).

The interface is implemented in Python using only standard libraries - no external dependencies required.

The main command is called "cbrain" and as is typical for such clients, works
with a set of subcommand and options (e.g. "cbrain file list -j") such as:
```bash
cbrain file list
cbrain project show
cbrain --json dataprovider list
```

## CBRAIN Access Options

There are two main ways to access CBRAIN:

1. **McGill Production Portal** (Recommended for Regular Users)
   - Access the McGill-supported CBRAIN production portal at: https://portal.cbrain.mcgill.ca/
   - No local installation required
   - Web-based interface for most common operations

2. **Custom/Development Setup**
   - Deploy CBRAIN on your lab cluster, cloud, or virtual machine
   - Suitable for organizations wanting their own CBRAIN instance
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

## Development

This is part of a GSoC (Google Summer of Code) project sponsored by [INCF](https://www.incf.org/).

The lead developer is [axif0](https://github.com/axif0), mentored by the developers of the CBRAIN project.

## License

See [LICENSE](LICENSE) file for details.
