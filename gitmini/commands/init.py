import os

def handle_init(args):
    gitmini_dir = '.gitmini'
    subdirs = ['objects', 'logs']
    index_file = 'index'

    if os.path.exists(gitmini_dir):
        print("GitMini repository already initialized.")
        return

    os.makedirs(gitmini_dir)
    for sub in subdirs:
        os.makedirs(os.path.join(gitmini_dir, sub))
    open(os.path.join(gitmini_dir, index_file), 'w').close()

    print("Initialized empty GitMini repository in .gitmini/")
