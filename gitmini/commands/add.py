import os
from gitmini.utils import find_gitmini_root, compute_sha1

def handle_add(args):
    """ Handles the 'add' command to stage files for later commits. """

    # Locate the GitMini repo root
    repo_root = find_gitmini_root()
    print(f"Located .gitmini repo at: {repo_root}")

    # Identify passed in files/folders for staging
    targets = args.targets if hasattr(args, 'targets') and args.targets else []

    if not targets:
        print("No files specified to add.")
        return

    all_files_to_stage = set()

    for target in targets:
        # Some path fixing stuff... idrk but it works
        abs_target_path = os.path.abspath(os.path.join(repo_root, os.path.relpath(target)))

        # Skip files in .gitmini
        if os.path.commonpath([abs_target_path, os.path.join(repo_root, ".gitmini")]) == os.path.join(repo_root, ".gitmini"):
            continue

        if os.path.isfile(abs_target_path):
            # Add a single file
            rel_path = os.path.relpath(abs_target_path, repo_root)
            all_files_to_stage.add(rel_path)

        elif os.path.isdir(abs_target_path):
            # Collect all files in a directory
            for root, dirs, files in os.walk(abs_target_path):
                # Prevent going into .gitmini
                dirs[:] = [d for d in dirs if os.path.join(root, d) != os.path.join(repo_root, ".gitmini")]

                for file in files:
                    file_path = os.path.join(root, file)
                    # Skip files inside .gitmini
                    if os.path.commonpath([file_path, os.path.join(repo_root, ".gitmini")]) == os.path.join(repo_root, ".gitmini"):
                        continue
                    # Add each file
                    rel_path = os.path.relpath(file_path, repo_root)
                    all_files_to_stage.add(rel_path)

        else:
            # Invalid input (nonexistent file/dir)
            print(f"Warning: '{target}' is not a valid file or directory. Skipping.")

    # Perform SHA-1 hashing and store blobs
    objects_dir = os.path.join(repo_root, ".gitmini", "objects")
    os.makedirs(objects_dir, exist_ok=True)

    staged_files = {}  # rel_path --> sha1 hash

    for rel_path in sorted(all_files_to_stage):
        abs_path = os.path.join(repo_root, rel_path)

        try:
            # Read file content for hashing
            with open(abs_path, "rb") as f:
                contents = f.read()
        except Exception as e:
            print(f"Error reading {rel_path}: {e}")
            continue

        # Compute blob hash
        sha1_hash = compute_sha1(contents)
        blob_path = os.path.join(objects_dir, sha1_hash)

        # Store blob if not already done
        if not os.path.exists(blob_path):
            try:
                with open(blob_path, "wb") as f:
                    f.write(contents)
            except Exception as e:
                print(f"Error writing blob for {rel_path}: {e}")
                continue

        # Track staged file and hash
        staged_files[rel_path] = sha1_hash

    for rel_path in sorted(staged_files.keys()):
        print(f"Added {rel_path}")
