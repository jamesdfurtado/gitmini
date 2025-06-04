import argparse

from gitmini.commands.init import handle_init
from gitmini.commands.add import handle_add
from gitmini.commands.commit import handle_commit
from gitmini.commands.log import handle_log
from gitmini.commands.checkout import handle_checkout

def main():
    # Main entry point for the GitMini CLI
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
    add_parser = subparsers.add_parser(     # Base command
        'add',
        help='Add files to staging area',
        description='Add specified files to GitMini\'s staging area for the next commit.'
    )
    add_parser.add_argument(                # Staging files, folders, or all
        'targets',
        nargs='*',
        help='Files or directories to add to staging area'
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
