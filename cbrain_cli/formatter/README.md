# Welcome to the CBRAIN CLI Formatter Layer!

This directory is all about **presentation**. Once a handler has domain data from the `data/` API layer, it hands that data to these formatters for terminal output.

These formatters are responsible for creating the clean tables, organized summaries, and human-readable text you see when you run a command.

## How It Fits Together 🧩

**Data there, Display here.**

While the `data/` directory handles backend API interactions, the `formatter/` directory focuses exclusively on presenting that info. Every `_fmt.py` file here perfectly matches a corresponding data module. For example, `tasks.py` gets the data, and `tasks_fmt.py` decides how to draw it on your screen!

## What the Formatter Actually Does 🪄

Imagine you ask CBRAIN for a list of your files using `cbrain file list`. The raw data coming from the server is a dense machine-readable bundle filled with IDs, timestamps, and metadata.

Instead of throwing that raw JSON at you, the formatter layer catches the data and turns it into a beautiful, easy-to-read table right in your terminal. Here is exactly what these scripts do:

**The Raw Data (what `data/` returns):**
```json
{"id": 1024, "type": "SingleFile", "name": "my_mri_scan.nii.gz"}
```

**The Formatted Output (what `formatter/` shows you for `cbrain file list`):**
```text
ID   Type       File Name
---- ---------- ------------------
1024 SingleFile my_mri_scan.nii.gz
```

*(Fun fact: We don't use heavy external libraries like `PrettyTable` or `Rich` for this! The CLI uses a custom-built, lightweight, dynamic table formatter powered completely by Python's built-in `textwrap` and `shutil` libraries. That means zero extra dependencies to slow you down!)*

### Raw JSON Output

Commands that return API data also support a `--json` flag that skips the
formatter and dumps the raw response. Useful for scripting or piping into
other tools. Session commands such as `login` and `logout` still print
plain text.

## The Formatter Files 🗂️

Each `_fmt.py` file knows exactly how to display its specific type of data:

* **`background_activities_fmt.py`**: Renders background job lists and individual activity details.
* **`data_providers_fmt.py`**: Renders data provider lists and full provider detail views.
* **`files_fmt.py`**: Renders file lists, file detail views, upload results, move/copy results, and delete confirmations.
* **`projects_fmt.py`**: Renders project lists, the current active project, full project details, the "no project" state, and unswitch results.
* **`remote_resources_fmt.py`**: Renders remote resource (bourreau) lists and individual resource details.
* **`tags_fmt.py`**: Renders tag lists, tag details, and create/update/delete operation results.
* **`tasks_fmt.py`**: Renders task lists, detailed task views, and bulk operation results.
* **`tool_configs_fmt.py`**: Renders tool configuration lists, config details, and Boutiques descriptors.
* **`tools_fmt.py`**: Renders tool lists and individual tool detail views.

Every formatter script is basically a tiny artist that knows exactly how to draw its specific type of data so it's perfectly readable for you!
