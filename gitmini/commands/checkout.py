import os
import sys

from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.HEAD import HEAD
from gitmini.classes.Index import Index

def handle_checkout(args):
    """
    Checkout a branch or specific commit.
    --force will discard any staged changes.
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    head = HEAD(repo)
    target = args.target

    # 1) resolve target: branch?
    heads_dir = os.path.join(repo.gitmini_dir, "refs", "heads")
    branch_file = os.path.join(heads_dir, target)
    if os.path.exists(branch_file):
        new_commit = open(branch_file, "r").read().strip()
        is_branch = True
    else:
        # commit hash?
        obj_file = os.path.join(repo.objects_dir, target)
        if os.path.exists(obj_file):
            new_commit = target
            is_branch = False
        else:
            print(f"fatal: branch or commit '{target}' not found", file=sys.stderr)
            sys.exit(1)

    # 2) if dirty and not forcing, bail
    index = Index(repo)
    if index.entries and not args.force:
        print("error: cannot switch branches with uncommitted changes")
        sys.exit(1)

    # 3) clean current tracked files
    current_commit = head.get_commit()
    current_tree = _get_tree_hash(repo, current_commit)
    _clean_working_dir(repo, current_tree)

    # 4) move HEAD
    if is_branch:
        head.set_ref(target)
    else:
        head.set_commit(new_commit)

    # 5) populate new snapshot
    tree_hash = _get_tree_hash(repo, new_commit)
    entries = _read_tree(repo, tree_hash)

    for blob_hash, rel_path in entries.items():
        src = os.path.join(repo.objects_dir, blob_hash)
        dst = os.path.join(repo.root, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, "rb") as sf, open(dst, "wb") as df:
            df.write(sf.read())

    # refresh index to match new tree
    new_index = Index(repo)
    new_index.entries = entries
    new_index.write()


def _get_tree_hash(repo, commit_hash):
    commit_path = os.path.join(repo.objects_dir, commit_hash)
    with open(commit_path, "rb") as f:
        lines = f.read().decode(errors="ignore").splitlines()
    for line in lines:
        if line.startswith("tree "):
            return line.split(" ", 1)[1].strip()
    return None

def _read_tree(repo, tree_hash):
    tree_path = os.path.join(repo.objects_dir, tree_hash)
    with open(tree_path, "rb") as f:
        lines = f.read().decode(errors="ignore").splitlines()
    entries = {}
    for line in lines:
        if not line:
            continue
        sha, path = line.split(" ", 1)
        entries[sha] = path
    return entries

def _clean_working_dir(repo, tree_hash):
    entries = _read_tree(repo, tree_hash)
    for rel_path in entries.values():
        full = os.path.join(repo.root, rel_path)
        if os.path.exists(full):
            os.remove(full)
