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
    Commits staged changes to the repository.

    First, it builds and writes a Tree (more on that in Tree.py),
    then it creates a Commit object.
    The Commit object contains the tree SHA, parent commit SHA (if any), and the commit message.
    
    Also, updates HEAD to point to the newly created commit.
    """

    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    index = Index(repo)

    if not index.entries:
        print("nothing to commit")
        sys.exit(1)

    # Create and write Tree object from index
    tree = Tree(repo, index.entries)
    tree_hash = tree.write()

    # Find last commit from HEAD
    head = HEAD(repo)
    parent_hash = head.value
    parent_tree_hash = None

    if parent_hash:
        parent_obj_path = os.path.join(repo.gitmini_dir, "objects", parent_hash)
        if os.path.exists(parent_obj_path):
            with open(parent_obj_path, "rb") as f:
                content = f.read().decode(errors="ignore")
                # First non-empty line should be "tree <parent_tree_hash>"
                for line in content.splitlines():
                    if line.startswith("tree "):
                        parent_tree_hash = line.split(" ", 1)[1].strip()
                        break

    # If there is a parent and the new tree is the same as the parent tree, there is "nothing to commit". :^)
    if parent_tree_hash and parent_tree_hash == tree_hash:
        print("nothing to commit")
        sys.exit(1)

    # Commit message
    message = args.message or ""

    # Create and write the commit object
    commit = Commit(repo, tree_hash, parent_hash, message)
    commit_hash = commit.write()

    # Update HEAD to newly created commit object
    head.set(commit_hash)

    commit_path = os.path.join(repo.gitmini_dir, "objects", commit_hash)
    print(f"Commit object written to: {commit_path}")


# This one was SO HARD!!!! But we did it