# GitMini

![PyPI](https://img.shields.io/pypi/v/gitmini)
![License](https://img.shields.io/github/license/jamesdfurtado/gitmini)

**GitMini** is a lightweight Version Control System built from scratch in Python. It replicates core non-remote Git commands like `init`, `add`, `commit`, `log`, `checkout`, and `branch`.

⭐ This project has been uploaded to **PyPI**! Find the link here: https://pypi.org/project/gitmini/

---

## 💪 Motivation
* Exercise in-depth DSA and OOP practices.
* Demystify Git and learn safe Version Control principles.
* Deploy a real-world package to PyPI adhering to PEP standards.
* Practice safe SDLC methods and continuously test during development.
* Build a CLI tool from scratch.
* Learn to efficiently store and search data.

---

## 🎥 Demo

### 🧱 Core Workflow (init, add, commit, .gitmini-ignore)

![Core Workflow](gifs/core.gif)

* Initializing a repository
* Staging (adding) changes
* Comitting files
* .gitmini-ignore support

<br><br>

🌿 Branching Workflow (log, branch, checkout)

![Branching Workflow](gifs/branch.gif)

* Checking commit logs
* Viewing current branch, creating new branch
* Checkout to branches and past commits

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

## 📦 Installation and Usage

**Make sure to create and activate a Python virtual environment before anything.**

GitMini is meant to be run inside an activated virtual environment -- it doesn’t add itself to PATH globally.

1. Navigate into your desired directory, then create & activate your virtual environment
   
```
cd project-root
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install 'gitmini' via pip

```
pip install gitmini
```

3. Initialize a GitMini repository.

```
gitmini init
```

This command will generate the repository (.gitmini/), and the .gitmini-ignore file

4. **Ensure that your virtual environment file is ignored** by adding it to the .gitmini-ignore file.

*If you do not do this, GitMini will track your venv, and the program could break.*

```
# Within .gitmini-ignore, type the following:
<your-virtual-environment>/
```

5. Create project files/folders as you please, then stage your changes.

*Any of the following commands can be used:*
```
# To add a specific file or folder:
gitmini add <file> <folder>

# To add all files in the repo: 
gitmini add .
```

6. Make your first commit!

```
gitmini commit -m "Initial commit"
```

And you're done! You can now freely use GitMini to track your files.

And just like Git, you can make a new `branch`, `checkout` to them, and view the commit `log`.

## 👤 Author

James David Furtado

jamesdfurtado@gmail.com

https://www.linkedin.com/in/james-furtado/

## 📄 License
MIT License. See LICENSE file for details.
