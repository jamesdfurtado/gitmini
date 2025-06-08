import os
import sys

from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.HEAD import HEAD

def handle_branch(args):
    """
    List all branches, or create a new branch pointing at HEAD.
    """
    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    heads_dir = os.path.join(repo.gitmini_dir, "refs", "heads")

    if args.name:
        # create new branch at current commit
        new_branch = args.name
        branch_file = os.path.join(heads_dir, new_branch)
        if os.path.exists(branch_file):
            print(f"fatal: branch '{new_branch}' already exists")
            sys.exit(1)
        commit_hash = HEAD(repo).get_commit()
        with open(branch_file, "w") as f:
            f.write(commit_hash)
    else:
        # list branches, mark current
        head = HEAD(repo)
        current_ref = head.get_ref()
        for b in sorted(os.listdir(heads_dir)):
            prefix = "*" if current_ref == f"refs/heads/{b}" else " "
            print(f"{prefix} {b}")
