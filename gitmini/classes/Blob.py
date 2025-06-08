import os
from gitmini.utils import compute_sha1

class Blob:
    """
    A blob stores the raw contents of a file.
    It does not contain the name or path of the file.
    It is created using the 'gitmini add' command.

    The blob is stored in the .gitmini/objects directory with its SHA-1 hash as the filename.
    In real git, the contents of the file are compressed, but for clarity and simplicity, we store the file's actual contents in it.
    """

    def __init__(self, repo, file_path):
        """
        repo: an instance of the "Repo" object, which is the .gitmini repository
        file_path: the path being added, relative to the repository root.
        """
        self.repo = repo
        self.file_path = file_path
        with open(os.path.join(repo.root, file_path), "rb") as f:
            self.content = f.read()
        self.sha1 = compute_sha1(self.content)

    def write(self):
        """
        Write the raw content into .gitmini/objects/<blob_sha1_hash> if not already there.
        Returns the SHA-1 string.
        """
        path = os.path.join(self.repo.objects_dir, self.sha1)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(self.content)
        return self.sha1



# Currently not compressing the file contents.
# This is okay for now for debugging purposes, but we need to implement that later.