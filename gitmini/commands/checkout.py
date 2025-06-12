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
    curr_tree_map = read_tree(repo, curr_tree)  # path → sha

    if not args.force and index.entries != curr_tree_map:
        print("error: cannot switch branches with uncommitted changes")
        sys.exit(1)

    # Load new tree for cleanup comparison
    new_tree = get_tree_hash(repo, new_commit)
    new_raw = read_tree(repo, new_tree)

    clean_working_dir(repo, curr_tree_map, new_raw)

    # Update HEAD
    if is_branch:
        head.set_ref(target)
    else:
        head.set_commit(new_commit)
        print(f"Note: checking out '{new_commit[:7]}'")
        print("You are in 'detached HEAD' state. Any commits you make will be orphaned unless you create a branch.")

    # Load file contents from the new commit's tree
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

    if is_branch:
        print(f"checked out to branch '{target}'")

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

def clean_working_dir(repo, old_tree_map, new_tree_map):
    # Delete files tracked in old_tree_map that are not in new_tree_map
    for path in old_tree_map:
        if path not in new_tree_map:
            abs_path = os.path.join(repo.root, path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
                # Recursively remove empty parent directories up to repo root
                parent = os.path.dirname(abs_path)
                while parent != repo.root and os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                    parent = os.path.dirname(parent)
