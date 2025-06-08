import os
import sys
from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.Index import Index
from gitmini.classes.Tree import Tree
from gitmini.classes.Commit import Commit
from gitmini.classes.HEAD import HEAD

def handle_commit(args):
    """
    Commit staged changes to the repository.
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    index = Index(repo)
    head = HEAD(repo)

    # Do not allow commits in detached HEAD state
    # TODO: change this. Research how git handles this.
    if head.is_detached():
        print("error: cannot commit in detached HEAD state.")
        print("Run: gitmini branch <name> to create a branch first.")
        sys.exit(1)

    if not index.entries:
        print("nothing to commit")
        sys.exit(1)

    # Build tree from index
    tree = Tree(repo, index.entries)
    tree_hash = tree.write()

    # Find parent commit
    parent_hash = head.get_commit()
    parent_tree = None
    if parent_hash:
        obj_path = os.path.join(repo.gitmini_dir, "objects", parent_hash)
        if os.path.exists(obj_path):
            with open(obj_path, "rb") as f:
                for line in f.read().decode(errors="ignore").splitlines():
                    if line.startswith("tree "):
                        parent_tree = line.split(" ", 1)[1].strip()
                        break

    # Compare for new changes
    if parent_tree and parent_tree == tree_hash:
        print("nothing to commit")
        sys.exit(1)

    message = args.message or ""

    # Write commit
    commit = Commit(repo, tree_hash, parent_hash, message)
    commit_hash = commit.write()

    # Update branch pointer
    head.update(commit_hash)

    # Reset index to match this commit's tree
    new_entries = {}
    tree_path = os.path.join(repo.objects_dir, tree_hash)
    with open(tree_path, "rb") as tf:
        for line in tf.read().decode(errors="ignore").splitlines():
            if not line:
                continue
            sha, path = line.split(" ", 1)
            new_entries[path] = sha

    index.entries = new_entries
    index.write()

    path = os.path.join(repo.gitmini_dir, "objects", commit_hash)
    print(f"Commit object written to: {path}")
