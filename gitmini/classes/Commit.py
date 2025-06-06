import os
import time
from gitmini.utils import compute_sha1

class Commit:
    """
    Points to a tree object and its parent commit (if any).
    Contains the following content:

        tree <tree_sha1>
        parent <parent_sha1>
        author <username> <timestamp>
        
        <commit message>
    """

    def __init__(self, repo, tree_hash, parent_hash=None, message=""):
        self.repo = repo
        self.tree_hash = tree_hash
        self.parent_hash = parent_hash
        self.message = message or ""
        self.author = os.getenv("GITMINI_AUTHOR", "").strip()      # May get rid of this later, seems unecessary for this project's sake
        self.timestamp = int(time.time())                          # This is not working right now.
        self.sha1 = None

    def write(self):
        """
        This function:
            1. Serializes the commit msg 
            2. computes SHA-1
            3. Writes to .gitmini/objects/
            4. Returns the commit’s SHA-1.
        """
        lines = []
        lines.append(f"tree {self.tree_hash}")
        
        if self.parent_hash:
            lines.append(f"parent {self.parent_hash}")
        if self.author:
            lines.append(f"author {self.author} {self.timestamp}")

        lines.append("")
        lines.append(self.message)
        content_str = "\n".join(lines)
        content_bytes = content_str.encode()

        self.sha1 = compute_sha1(content_bytes)
        object_path = os.path.join(self.repo.objects_dir, self.sha1)
        if not os.path.exists(object_path):
            with open(object_path, "wb") as out:
                out.write(content_bytes)
        return self.sha1
