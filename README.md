# GitMini

**GitMini** is a lightweight, minimal version control system built from scratch in Python. It replicates core Git commands like `init`, `add`, `commit`, `log`, and `checkout` — perfect for learning how Git works under the hood or experimenting with your own VCS.

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

```
pip install gitmini
```


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
GitHub : https://github.com/jamesdfurtado

## 📄 License
MIT License. See LICENSE file for details.