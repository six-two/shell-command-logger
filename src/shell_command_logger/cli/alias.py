#!/usr/bin/env python3
# Call me like this: "scl-alias --print bash | source"
# This does not seem to work in zsh. Workaround: "scl-alias -p zsh > /tmp/zsh && source /tmp/zsh"
import argparse
import os
import sys
# import the code from this package
from shell_command_logger.alias import print_text_to_source, load_alias_file, save_alias_file, CONFIG_FILE

SUBCOMMAND_NAMES = ["a", "alias"]
ARG_PARSER_OPTIONS = {
    "description": "This command can be used to manage aliases, which can be used to automatcally log the output of specified binaries",
    "help": "manage aliases",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    mutex = ap.add_mutually_exclusive_group()
    mutex.add_argument("-p", "--print", metavar=("shell"), choices=["bash", "fish", "zsh"], help="print the commands to create the aliases for the given shell. This can be directly piped into `source`")
    mutex.add_argument("-s", "--set", nargs="*", help="overwrites the alias list with the given values. This deletes all old entries")
    mutex.add_argument("-a", "--add", nargs="+", help="add the given programs to the alias list")
    mutex.add_argument("-d", "--delete", nargs="+", help="delete the given programs from the alias list")
    mutex.add_argument("--reset", action="store_true", help="reset the alias list back to the default value")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    if args.print:
        shell = args.print
        print_text_to_source(shell)
    elif args.set is not None:
        save_alias_file(args.set)
    elif args.add:
        programs = load_alias_file()
        programs += args.add
        save_alias_file(programs)
    elif args.delete:
        programs = load_alias_file()
        programs = [x for x in programs if x not in args.delete]
        save_alias_file(programs)
    elif args.reset:
        os.remove(CONFIG_FILE)
    else:
        for program in load_alias_file():
            print(program)

    # By default return 0 (success)
    return 0


def _main():
    # Parse arguments
    ap = argparse.ArgumentParser(**ARG_PARSER_OPTIONS)
    populate_agrument_parser(ap)
    args = ap.parse_args()

    # Run the main function
    exit_code = subcommand_main(args)

    # And exit
    sys.exit(exit_code)

if __name__ == "__main__":
    _main()

