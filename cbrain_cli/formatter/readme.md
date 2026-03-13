# Welcome to the CBRAIN CLI Formatter Layer! 🎨

This directory is all about **presentation**. Once the CLI fetches raw data objects from the CBRAIN backend (using the `data/` modules), it hands them over to these formatter scripts to make them look great in your terminal.

These formatters are responsible for creating the clean tables, organized summaries, and human-readable text you see when you run a command.

## How It Fits Together 🧩

**Data there, Display here.**

While the `data/` directory handles backend API interactions, the `formatter/` directory focuses exclusively on presenting that info. Every `_fmt.py` file here perfectly matches a corresponding data module. For example, `tasks.py` gets the data, and `tasks_fmt.py` decides how to draw it on your screen!

## What the Formatter Actually Does 🪄

Imagine you ask CBRAIN for a list of your files using `cbrain file list`. The raw data coming from the server is a dense machine-readable bundle filled with IDs, timestamps, and metadata.

Instead of throwing that raw JSON at you, the formatter layer catches the data and turns it into a beautiful, easy-to-read table right in your terminal. Here is exactly what these scripts do:

**The Raw Data (what `data/` gets):**
```json
{"id": 1024, "name": "my_mri_scan.nii.gz", "size": 47185920, "status": "synced"}
```

**The Formatted Output (what `formatter/` shows you):**
```text
+---------+----------------------+---------+-------------+
| File ID | Name                 | Size    | Status      |
+---------+----------------------+---------+-------------+
| 1024    | my_mri_scan.nii.gz   | 45.0 MB | Synced      |
+---------+----------------------+---------+-------------+
```

*(Fun fact: We don't use heavy external libraries like `PrettyTable` or `Rich` for this! The CLI uses a custom-built, lightweight, dynamic table formatter powered completely by Python's built-in `textwrap` and `shutil` libraries. That means zero extra dependencies to slow you down!)*

Every `_fmt.py` script in this folder is basically a tiny artist that knows exactly how to draw its specific type of data so it's perfectly readable for you!
