import os
import sys

from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.HEAD import HEAD
from gitmini.classes.Index import Index

def handle_checkout(args):
    """
    Switch to a branch or a specific commit.
    --force will discard any staged/uncommitted changes.
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    head = HEAD(repo)
    target = args.target

    # Resolve branch command
    heads_dir = os.path.join(repo.gitmini_dir, "refs", "heads")
    branch_file = os.path.join(heads_dir, target)
    if os.path.exists(branch_file):
        new_commit = open(branch_file, "r").read().strip()
        is_branch = True
    else:
        # Pull commit hash
        obj_file = os.path.join(repo.objects_dir, target)
        if os.path.exists(obj_file):
            new_commit = target
            is_branch = False
        else:
            print(f"fatal: branch or commit '{target}' not found", file=sys.stderr)
            sys.exit(1)

    # Checkout is not allowed unless project is fully committed, or --force is used
    index = Index(repo)
    current_commit = head.get_commit()
    curr_tree = get_tree_hash(repo, current_commit)
    tree_map = read_tree(repo, curr_tree)  # path → sha

    if not args.force and index.entries != tree_map:
        print("error: cannot switch branches with uncommitted changes")
        sys.exit(1)

    clean_working_dir(repo, curr_tree)

    # Update HEAD
    if is_branch:
        head.set_ref(target)
    else:
        head.set_commit(new_commit)

    # Load file contents from the new commit's tree
    new_tree = get_tree_hash(repo, new_commit)
    new_raw = read_tree(repo, new_tree)

    for path, sha in new_raw.items():
        src = os.path.join(repo.objects_dir, sha)
        dst = os.path.join(repo.root, path)
        if not os.path.exists(src):
            print(f"fatal: object file for {path} ({sha}) not found", file=sys.stderr)
            sys.exit(1)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, "rb") as sf, open(dst, "wb") as df:
            df.write(sf.read())

    # Refresh index to match the new tree
    new_index = Index(repo)
    new_index.entries = dict(new_raw)
    new_index.write()


def get_tree_hash(repo, commit_hash):
    # Extracts the tree hash from a commit object
    commit_path = os.path.join(repo.objects_dir, commit_hash)
    with open(commit_path, "rb") as f:
        for line in f.read().decode(errors="ignore").splitlines():
            if line.startswith("tree "):
                return line.split(" ", 1)[1].strip()
    return None

def read_tree(repo, tree_hash):
    # Loads a tree object and returns key-value pairs of paths and hashes
    tree_path = os.path.join(repo.objects_dir, tree_hash)
    with open(tree_path, "rb") as f:
        lines = f.read().decode(errors="ignore").splitlines()
    entries = {}
    for line in lines:
        if not line:
            continue
        sha, path = line.split(" ", 1)
        entries[path] = sha
    return entries

def clean_working_dir(repo, tree_hash):
    # Removes files that are not in tree from CWD
    for path in read_tree(repo, tree_hash).keys():
        full = os.path.join(repo.root, path)
        if os.path.exists(full):
            os.remove(full)
