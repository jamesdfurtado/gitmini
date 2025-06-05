import os
from gitmini.utils import find_gitmini_root

def handle_commit(args):
    """ Handles the 'commit' command to record a new commit from staged files. """

    # Locate the GitMini repo root
    repo_root = find_gitmini_root()
    print(f"Located .gitmini repo at: {repo_root}")

    # Check for existing index
    index_path = os.path.join(repo_root, ".gitmini", "index")
    if not os.path.exists(index_path):
        print("Nothing to commit: staging area is missing.")
        return

    # Read index and ensure it has content
    with open(index_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("Nothing to commit: staging area is empty.")
        return

    print("Staged files found. Proceeding with commit...")
