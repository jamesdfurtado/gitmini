import argparse

from gitmini.commands.init import handle_init
from gitmini.commands.add import handle_add
from gitmini.commands.commit import handle_commit
from gitmini.commands.log import handle_log
from gitmini.commands.checkout import handle_checkout
from gitmini.commands.branch import handle_branch
from gitmini.commands.login import handle_login
from gitmini.commands.remote.add import handle_remote_add
from gitmini.commands.remote.branch import handle_remote_branch
from gitmini.commands.push import handle_push

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

    # login
    login_p = subparsers.add_parser('login', help='Authenticate with GitMiniHub via browser')
    login_p.set_defaults(func=handle_login)

    # remote (parent command)
    remote_p = subparsers.add_parser('remote', help='Manage remotes')
    remote_subparsers = remote_p.add_subparsers(dest='remote_command')
    remote_p.set_defaults(func=lambda args: remote_p.print_help())

    # remote add
    remote_add_p = remote_subparsers.add_parser('add', help='Add a new remote repository')
    remote_add_p.add_argument('repository', help='Repository name')
    remote_add_p.set_defaults(func=handle_remote_add)

    # remote branch (future feature)
    remote_branch_p = remote_subparsers.add_parser('branch', help='Add a new remote branch (future feature)')
    remote_branch_p.add_argument('branch_name', help='Name of new remote branch')
    remote_branch_p.set_defaults(func=handle_remote_branch)

    # push
    push_p = subparsers.add_parser('push', help='Push local branch to remote')
    push_p.add_argument('branch', nargs='?', help='[<local-branch>:]<remote-branch> (if omitted, sends data from current local branch to remote branch equivelant.)')
    push_p.set_defaults(func=handle_push)

    args = parser.parse_args()
    args.func(args)
