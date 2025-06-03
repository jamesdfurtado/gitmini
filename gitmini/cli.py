import argparse

def main():
    parser = argparse.ArgumentParser(
        prog='gitmini',
        description='GitMini – A lightweight version control system'
    )

    # Prepare for subcommands (empty for now)
    subparsers = parser.add_subparsers(dest='command')
    
    # If no command is provided
    parser.set_defaults(func=lambda args: parser.print_help())

    args = parser.parse_args()
    args.func(args)
