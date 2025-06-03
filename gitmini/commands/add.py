from gitmini.utils import find_gitmini_root

def handle_add(args):
    """ Handles the 'add' command to stage files for later commits. """
    
    repo_root = find_gitmini_root()
    print(f"Located .gitmini repo at: {repo_root}")
