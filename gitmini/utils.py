import os
import sys

def find_gitmini_root():
    """Walks up from the current directory to locate the .gitmini directory."""
    
    current_dir = os.getcwd()
    while True:
        potential_gitmini = os.path.join(current_dir, ".gitmini")
        if os.path.isdir(potential_gitmini):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            print("fatal: not a gitmini repository (or any of the parent directories): .gitmini", file=sys.stderr)
            sys.exit(1)
        current_dir = parent_dir
