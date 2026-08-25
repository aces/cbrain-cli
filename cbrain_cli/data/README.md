# Welcome to the CBRAIN CLI Data Layer! 👋

This directory is the core engine connecting our command-line tools to **CBRAIN**—a powerful web-enabled platform built to manage large, distributed research datasets and mediate high-performance computing (HPC) tasks.

Whenever the CLI needs to talk to CBRAIN's architecture (specifically the **BrainPortal** API), it happens right here.

## How It Is Used 🛠️

Think of these Python modules as your direct bridge to CBRAIN's resources. They handle BrainPortal API interactions — reads and writes — plus client-side validation. If a user command needs the CBRAIN API, these modules do the heavy lifting.

### The Modules at a Glance (with Example Commands!):

* **`background_activities.py`**: Tracks backend jobs in progress (`cbrain background`).
  * `cbrain background list`
  * `cbrain background show 42`

* **`data_providers.py`**: Connects to the systems storing your research data (`cbrain data-provider`).
  * `cbrain data-provider list`
  * `cbrain data-provider show 15`
  * `cbrain data-provider is-alive 15`
  * `cbrain data-provider delete-unregistered-files 15`

* **`files.py`**: Manages data uploads, caching, and transfers across CBRAIN (`cbrain file`).
  * `cbrain file list`
  * `cbrain file show 99`
  * `cbrain file upload /path/to/file.nii --data-provider-id 15 --group-id 3`
  * `cbrain file copy --file-id 2 3 --data-provider-id 15`
  * `cbrain file move --file-id 2 --data-provider-id 15`
  * `cbrain file delete 99`

* **`projects.py`**: Keeps user research organized (`cbrain project`).
  * `cbrain project list`
  * `cbrain project show 10`
  * `cbrain project switch 10`
  * `cbrain project switch all`
  * `cbrain project unswitch`

* **`remote_resources.py`**: Interfaces with bourreaux / execution servers (`cbrain remote-resource`).
  * `cbrain remote-resource list`
  * `cbrain remote-resource show 5`

* **`tags.py`**: Organizes and categorizes files and tasks (`cbrain tag`).
  * `cbrain tag list`
  * `cbrain tag show 7`
  * `cbrain tag create --name NewTag1 --user-id 2 --group-id 3`
  * `cbrain tag update 7 --name UpdatedTag --user-id 2 --group-id 3`
  * `cbrain tag delete 7`

* **`tasks.py`**: Orchestrates intensive compute jobs on remote HPCs (`cbrain task`).
  * `cbrain task list`
  * `cbrain task list bourreau-id 4`
  * `cbrain task show 2`
  * `cbrain task operation hold --task-id 2`
  * `cbrain task operation terminate --task-id 1 2`
  * `cbrain --debug task list`

* **`tools.py` & `tool_configs.py`**: Manages the scientific tools available on CBRAIN (`cbrain tool` / `cbrain tool-config`).
  * `cbrain tool list`
  * `cbrain tool show 8`
  * `cbrain tool-config list`
  * `cbrain tool-config show 12`
  * `cbrain tool-config boutiques-descriptor 12`

## How It Fits Together 🧩

**API here, Display there.**

**API interaction layer**: GET/list/show plus state-changing calls (upload, delete, move/copy, tag create/update/delete, project switch/unswitch, task operations, and similar). Modules talk to BrainPortal via `CbrainClient`, validate inputs, and return domain data (or raise typed errors). They do not print. Handlers pass results to `formatter/` for terminal output.
