import os
from gitmini.utils import find_gitmini_root

def handle_add(args):
    """ Handles the 'add' command to stage files for later commits. """

    # Locate the GitMini repo root
    repo_root = find_gitmini_root()
    print(f"Located .gitmini repo at: {repo_root}")

    # Identify passed in files/folders for staging
    targets = args.targets if hasattr(args, 'targets') and args.targets else []

    # If no files specified:
    if not targets:
        print("No files specified to add.")
        return

    all_files_to_stage = set()

    for target in targets:
        # Normalize path relative to repo root
        abs_target_path = os.path.abspath(os.path.join(os.getcwd(), target))

        # If target is a file:
        if os.path.isfile(abs_target_path):
            rel_path = os.path.relpath(abs_target_path, repo_root)
            if not rel_path.startswith(".gitmini/"):
                all_files_to_stage.add(rel_path)

        # If target is a directory:
        elif os.path.isdir(abs_target_path):
            for root, dirs, files in os.walk(abs_target_path):
                # Skip the .gitmini directory
                dirs[:] = [d for d in dirs if d != ".gitmini"]

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_root)
                    if not rel_path.startswith(".gitmini/"):
                        all_files_to_stage.add(rel_path)

        else:
            print(f"Warning: '{target}' is not a valid file or directory. Skipping.")

    # Print staged files
    # Currently, nothing is actually staged. Files are just identified.
    print("Files to stage:")
    for path in sorted(all_files_to_stage):
        print(f"  {path}")
