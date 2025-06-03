import argparse

def main():
    parser = argparse.ArgumentParser(
        prog='gitmini',
        description='GitMini – A lightweight version control system'
    )
    subparsers = parser.add_subparsers(dest='command')
    parser.set_defaults(func=lambda args: parser.print_help())


    """ SUBCOMMANDS """

    # init
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize a new GitMini repository',
        description='Initialize a new GitMini repository in the current directory.'
    )
    init_parser.set_defaults(func=handle_init)

    # add
    add_parser = subparsers.add_parser(
        'add',
        help='Add files to staging area',
        description='Add specified files to GitMini\'s staging area for the next commit.'
    )
    add_parser.set_defaults(func=handle_add)

    # commit
    commit_parser = subparsers.add_parser(
        'commit',
        help='Commit staged changes',
        description='Record a new commit with the current staged files.'
    )
    commit_parser.set_defaults(func=handle_commit)

    # log
    log_parser = subparsers.add_parser(
        'log',
        help='Show commit history',
        description='Display the commit history of the current GitMini repository.'
    )
    log_parser.set_defaults(func=handle_log)

    # checkout
    checkout_parser = subparsers.add_parser(
        'checkout',
        help='Checkout a previous commit',
        description='Restore files to the state of a previous commit.'
    )
    checkout_parser.set_defaults(func=handle_checkout)

    args = parser.parse_args()
    args.func(args)



""" COMMAND STUBS """

def handle_init(args):
    print('Init not implemented yet')

def handle_add(args):
    print('Add not implemented yet')

def handle_commit(args):
    print('Commit not implemented yet')

def handle_log(args):
    print('Log not implemented yet')

def handle_checkout(args):
    print('Checkout not implemented yet')
