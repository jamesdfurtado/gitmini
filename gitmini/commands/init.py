import os
import sys
from gitmini_core.classes.Repo import Repo

def handle_init(args):
    """
    Creates a new .gitmini/ directory in the current working directory.
    """
    cwd = os.getcwd()
    Repo.init(cwd)
