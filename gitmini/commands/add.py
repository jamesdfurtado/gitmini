import os
import sys
from gitmini.utils import find_gitmini_root
from gitmini.classes.Repo import Repo
from gitmini.classes.Blob import Blob
from gitmini.classes.Index import Index

def handle_add(args):
    """
    Stages newly added or changed files.
    Just like git, can be used with <file>, <dir>, or "."
    """

    repo_root = find_gitmini_root()
    repo = Repo(repo_root)
    index = Index(repo)

    cwd = os.getcwd()
    targets = args.targets
    if not targets:
        print("Nothing specified, nothing added.")
        sys.exit(1)

    # Create a list of filepaths
    to_stage = []

    if len(targets) == 1 and targets[0] == ".":
        # Use command relative to the current working directory
        base_dir = cwd
        for root, dirs, files in os.walk(base_dir):
            if ".gitmini" in dirs:
                dirs.remove(".gitmini")
            for file in files:
                abs_path = os.path.join(root, file)
                # Determine relative path to the repo root
                rel_path = os.path.relpath(abs_path, repo_root)
                to_stage.append(rel_path)
    else:
        for t in targets:
            abs_t = os.path.join(cwd, t)
            if os.path.isdir(abs_t):
                # Walk up the directory (AVOIDS .gitmini)
                for root, dirs, files in os.walk(abs_t):
                    if ".gitmini" in dirs:
                        dirs.remove(".gitmini")
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, repo_root)
                        to_stage.append(rel_path)
            elif os.path.isfile(abs_t):
                rel_path = os.path.relpath(abs_t, repo_root)
                to_stage.append(rel_path)
            else:
                print(f"warning: pathspec '{t}' did not match any files", file=sys.stderr)

    # Track whether anything actually changed
    changed = False

    # For each file in to_stage, compute its SHA-1, write a Blob if needed, update Index
    for rel_path in to_stage:
        abs_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(abs_path):
            continue

        # Create Blob
        blob = Blob(repo, rel_path)
        sha1 = blob.sha1

        # Avoid recreating blob if already exists. YAY CACHING!
        if index.entries.get(rel_path) == sha1:
            continue

        # Else, create blob and add to index
        blob.write()
        index.add(rel_path, sha1)
        changed = True

    if not changed:
        print("nothing to add")
        sys.exit(0)

    # Finalize index
    index.write()
