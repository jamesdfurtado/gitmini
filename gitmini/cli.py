import argparse

from gitmini.commands.init import handle_init
from gitmini.commands.add import handle_add
from gitmini.commands.commit import handle_commit
from gitmini.commands.log import handle_log
from gitmini.commands.checkout import handle_checkout
from gitmini.commands.branch import handle_branch

def main():

    # Main entry point for the GitMini CLI
    parser = argparse.ArgumentParser(
        prog='gitmini',
        description='GitMini – A lightweight version control system'
    )
    subparsers = parser.add_subparsers(dest='command')
    parser.set_defaults(func=lambda args: parser.print_help())

    # init
    init_p = subparsers.add_parser('init', help='Initialize a new GitMini repository')
    init_p.set_defaults(func=handle_init)

    # add
    add_p = subparsers.add_parser('add', help='Add files to staging area')
    add_p.add_argument('targets', nargs='*', help='Files or dirs to add')
    add_p.set_defaults(func=handle_add)

    # commit
    commit_p = subparsers.add_parser('commit', help='Commit staged changes')
    commit_p.add_argument('-m', '--message', help='Commit message', required=False)
    commit_p.set_defaults(func=handle_commit)

    # log
    log_p = subparsers.add_parser('log', help='Show commit history')
    log_p.set_defaults(func=handle_log)

    # checkout
    co_p = subparsers.add_parser('checkout',
                                 help='Switch to branch or commit',
                                 description='Restore working tree to branch tip or specific commit')
    co_p.add_argument('target', help='Branch name or commit hash')
    co_p.add_argument('--force', action='store_true',
                      help='Discard uncommitted changes and force checkout')
    co_p.set_defaults(func=handle_checkout)

    # branch
    br_p = subparsers.add_parser('branch',
                                 help='List or create branches',
                                 description='List branches, or create one if you specify a name')
    br_p.add_argument('name', nargs='?', help='Name of new branch')
    br_p.set_defaults(func=handle_branch)

    args = parser.parse_args()
    args.func(args)
