# GitMini

**GitMini** is a lightweight, minimal version control system built from scratch in Python. It replicates core Git commands like `init`, `add`, `commit`, `log`, and `checkout` — perfect for learning how Git works under the hood or experimenting with your own VCS.

This project has been uploaded to **PyPI**! Find the link here: https://pypi.org/project/gitmini/

---

## 🛠️ Features

- `gitmini init` – Initialize a new GitMini repository  
- `gitmini add` – Stage changes (individual files, folders, or `.`)  
- `gitmini commit` – Commit staged changes  
- `gitmini log` – View commit history  
- `gitmini checkout` – Switch between branches or restore old versions  
- Simple `.gitmini-ignore` support  
- Content-addressable storage using SHA-1  
- No external dependencies

---

## 📦 Installation

**Make sure to create and activate a python virtual environment before doing this.**

GitMini is not designed to work as a PATH variable.

1. Create and activate virtual environment
   
```
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install 'gitmini' via pip

```
pip install gitmini
```

Installation done!

## 📚 Usage

gitmini init

gitmini add file.txt

gitmini commit -m "Initial commit"

gitmini log

gitmini checkout <commit-hash or branch-name>

gitmini branch <new-branch>     (or, just leave without <new-branch> to see current branch)

## 👤 Author
James David Furtado

LinkedIn : https://www.linkedin.com/in/james-furtado/

## 📄 License
MIT License. See LICENSE file for details.
