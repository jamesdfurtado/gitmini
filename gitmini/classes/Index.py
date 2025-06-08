import os

class Index:
    """
    The Index is where we stage our added changes before committing.
    It is stored at .gitmini/index
    It contains a list of blob hashes and their corresponding file paths.
    """

    def __init__(self, repo):
        self.repo = repo
        self.index_file = os.path.join(repo.gitmini_dir, "index")
        # Load the index's entries
        self.entries = {}  # { filepath: blob_hash }
        if os.path.exists(self.index_file):
            with open(self.index_file, "r") as f:
                for line in f.readlines():
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    sha1, path = line.split(" ", 1)
                    self.entries[path] = sha1

        # Prune nonexistent files from index
        for path in list(self.entries.keys()):
            full = os.path.join(repo.root, path)
            if not os.path.isfile(full):
                del self.entries[path]

    def add(self, rel_path, sha1):
        """
        Stage a file and record that <rel_path> --> <sha1>.
        """
        self.entries[rel_path] = sha1

    def write(self):
        """
        Overhaul the index with relevant entries.
        This is for when a file is deleted, or its filename changes (essentially deletion).
        """
        with open(self.index_file, "w") as f:
            for path, sha1 in sorted(self.entries.items()):
                f.write(f"{sha1} {path}\n")
