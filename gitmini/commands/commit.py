import os
from datetime import datetime
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

    # Parse index lines into (hash, path) pairs
    staged_entries = []
    for line in lines:
        try:
            hash_val, rel_path = line.split(" ", 1)
            staged_entries.append((hash_val, rel_path))
        except ValueError:
            print(f"Skipping malformed index entry: {line}")

    # ----- Phase 3: Prepare Commit Metadata -----

    # Get parent commit hash if HEAD exists
    head_path = os.path.join(repo_root, ".gitmini", "HEAD")
    parent_hash = None
    if os.path.exists(head_path):
        with open(head_path, "r") as f:
            parent_hash = f.read().strip()

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Get commit message
    import sys

    if args.message:
        message = args.message.strip()
    else:
        if not sys.stdin.isatty():
            print("Error: commit message required in non-interactive mode.")
            return
        message = input("Enter commit message: ").strip()

    if not message:
        print("Aborting commit: empty message.")
        return


    # Construct commit object as a string
    lines = []
    if parent_hash:
        lines.append(f"parent {parent_hash}")
    lines.append(f"date {timestamp}")
    lines.append(f"message {message}")
    lines.append("")  # blank line
    for hash_val, path in staged_entries:
        lines.append(f"{hash_val} {path}")

    commit_contents = "\n".join(lines)
    print("\n--- Commit Content Preview ---")
    print(commit_contents)
    print("------------------------------")
