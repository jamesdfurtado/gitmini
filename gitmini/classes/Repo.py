import os
import sys

class Repo:
    """
    Holds all of the .gitmini repository's goodies.
    Contains a method to initialize a new .gitmini repository.
    """

    def __init__(self, path=None):
        # If path is given, use it as repo root
        if path:
            self.root = path
        else:
            # Else, find the root by walking up current directory
            from gitmini.utils import find_gitmini_root
            self.root = find_gitmini_root()

        self.gitmini_dir = os.path.join(self.root, ".gitmini")
        self.objects_dir = os.path.join(self.gitmini_dir, "objects")
        self.index_file = os.path.join(self.gitmini_dir, "index")
        self.head_file = os.path.join(self.gitmini_dir, "HEAD")

    @staticmethod
    def init(path):
        """
        Set up a .gitmini/ repository
        Will fail if one already exists.
        """
        gitmini_dir = os.path.join(path, ".gitmini")
        if os.path.exists(gitmini_dir):
            print(f"fatal: reinitialized existing GitMini repository in {gitmini_dir}")
            sys.exit(1)

        os.makedirs(gitmini_dir)
        os.makedirs(os.path.join(gitmini_dir, "objects"))
        # Create an empty index file
        open(os.path.join(gitmini_dir, "index"), "w").close()
        # Create an empty HEAD file
        open(os.path.join(gitmini_dir, "HEAD"), "w").close()

        print(f"Initialized empty GitMini repository in {gitmini_dir}")
