# Welcome to the CBRAIN CLI Data Layer! 👋

This directory is the core engine connecting our command-line tools to **CBRAIN**—a powerful web-enabled platform built to manage large, distributed research datasets and mediate high-performance computing (HPC) tasks.

Whenever the CLI needs to talk to CBRAIN's architecture (specifically the **BrainPortal** API), it happens right here.

## How It Is Used 🛠️

Think of these Python modules as your direct bridge to CBRAIN's resources. They handle all the API calls, data fetching, and object modeling. If a user command needs to interact with the CBRAIN database, these modules do the heavy lifting.

### The Modules at a Glance (with Example Commands!):

* **`background_activities.py`**: Tracks backend jobs in progress (`cbrain background`).
  * *Example:* `cbrain background list`
* **`data_providers.py`**: Connects to the systems storing your research data (`cbrain dataprovider`).
  * *Example:* `cbrain dataprovider show 15`
* **`files.py`**: Manages data uploads, caching, and transfers across CBRAIN (`cbrain file`).
  * *Example:* `cbrain file move --file-id 2 --dp-id 15`
* **`projects.py`**: Keeps user research organized (`cbrain project`).
  * *Example:* `cbrain project switch 10`
* **`remote_resources.py`**: Interfaces with external network capabilities (`cbrain remote-resource`).
  * *Example:* `cbrain remote-resource list`
* **`tags.py`**: Organizes and categorizes files and tasks (`cbrain tag`).
  * *Example:* `cbrain tag create --name NewTag1 --user-id 2 --group-id 3`
* **`tasks.py`**: Orchestrates intensive compute jobs on remote HPCs (`cbrain task`).
  * *Example:* `cbrain task show 2`
* **`tools.py` & `tool_configs.py`**: Manages the scientific tools available on CBRAIN (`cbrain tool` / `cbrain tool-config`).
  * *Example:* `cbrain tool list`

## How It Fits Together 🧩

**Data here, Display there.**

This folder is strictly for fetching raw objects from the CBRAIN server. Once we pull the data, we hand it off to the `formatter/` directory, which takes those raw responses and turns them into clean, human-readable outputs for your terminal!
