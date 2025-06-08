import os
from gitmini.utils import compute_sha1

class Tree:
    """
    A tree represents a "snapshot" of the project at the time of the commit.
    It is built strictly from the Index's blob-file mapping.

    It is stored under .gitmini/objects and named <tree_sha1_hash>. (The contents are just the index at the time)
    """

    def __init__(self, repo, index_entries):
        """
        repo: an instance of the "Repo" object, which is the .gitmini repository
        index_entries: a key-pair entry of blob hashes to files paths.
        """
        self.repo = repo
        self.entries = index_entries  # { filepath: blob_hash }
        self.sha1 = None

    def write(self):
        """
        This function:
            1. Builds the Tree's content
            2. Computes its SHA-1
            3. Writes it in .gitmini/objects/
            4. Returns the tree's SHA-1.
        """
        # Sort by filepath
        lines = []
        for path, blob_hash in sorted(self.entries.items()):
            lines.append(f"{blob_hash} {path}")

        # Append the index entries as <blob_hash> <file_path>
        lines = []
        for filepath, blob_hash in sorted(self.entries.items()):
            lines.append(f"{blob_hash} {filepath}")

        content_bytes = "\n".join(lines).encode()
        self.sha1 = compute_sha1(content_bytes)

        object_path = os.path.join(self.repo.objects_dir, self.sha1)
        if not os.path.exists(object_path):
            with open(object_path, "wb") as out:
                out.write(content_bytes)
        return self.sha1



# Stored in objects/ as <tree_sha1_hash>
# The contents of that file should be something like:

# 3adb33f1e2a3bc4f4d3ef7ad3abf8e03ec5cd102    file1.txt
# 9ba58d5fcd2cc4a9d17e51e8c25c6c9d263f95c7    script.sh

# <object_hash> <file_path>