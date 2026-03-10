# GitMini

![PyPI](https://img.shields.io/pypi/v/gitmini)
![License](https://img.shields.io/github/license/jamesdfurtado/gitmini)

**GitMini** is a lightweight, pip-installable CLI version control system built from scratch in Python.
It supports core Git commands: `init`, `add`, `commit`, `log`, `checkout`, `branch`

I built this project to: 
* understand Git's core system architecture.
* build a CLI tool from scratch.
* build a complex, object-oriented, modular system.

The data structures that powers this CLI can be found here: https://github.com/jamesdfurtado/gitmini-core

⭐ This project has been uploaded to **PyPI**! Find the link here: https://pypi.org/project/gitmini/


---

## 🛠️ Features & Demonstration

### Init and Add

* `gitmini init`
* `gitmini add`

Watch as the `.gitmini/` folder is populated in real-time:

![init/add](gifs/init_and_add.gif)

<hr style="height:1px; background-color:#ddd; border:none; margin:12px 0;" />

### Commit

* `gitmini commit`

Watch as the `HEAD` and `main` branch pointer are updated:

![commit](gifs/commit.gif)

<hr style="height:1px; background-color:#ddd; border:none; margin:12px 0;" />

### Branch and Checkout

* `gitmini branch`
* `gitmini checkout <branch-name>`

Watch as the `refs/heads` folder is populated with `new-branch`, and the `HEAD` file changes to point to `new-branch`:

![branch_checkout](gifs/branch_checkout.gif)

<hr style="height:1px; background-color:#ddd; border:none; margin:12px 0;" />

### Log

* `gitmini log`

Watch as each commit's contents are loaded into the codebase:

![log](gifs/log.gif)

<hr style="height:1px; background-color:#ddd; border:none; margin:12px 0;" />

### Ignore file

* `.gitmini-ignore`

Watch as I stage files, but `ignore_me.py` is not included.

![ignore](gifs/ignore.gif)


---


## 👤 Author

James David Furtado

jamesdfurtado@gmail.com

https://www.linkedin.com/in/james-furtado/

## 📄 License
MIT License. See LICENSE file for details.
