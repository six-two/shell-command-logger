#!/usr/bin/env python3
# Call me like this: "scl-alias --print bash | source"
# This does not seem to work in zsh. Workaround: "scl-alias -p zsh > /tmp/zsh && source /tmp/zsh"
import argparse
import os
import sys
# import the code from this package
from shell_command_logger.replay import select_file, select_command, remove_extension, replay_command
from shell_command_logger.config import load_config, sanitize_config, SclConfig


SUBCOMMAND_NAMES = ["r", "replay"]
ARG_PARSER_OPTIONS = {
    "description": "This subcommand can be used to replay any command output you have recorded with scl",
    "help": "replay a recorded command",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    mutex = ap.add_mutually_exclusive_group()
    mutex.add_argument("-i", "--input", metavar=("path"), help="the input file containing the command output")
    mutex.add_argument("-f", "--select-file", action="store_true", help="interactively search the file names")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    scl_config = sanitize_config(load_config())

    if args.input:
        path = args.input
    elif args.select_file:
        path = select_file(scl_config)
    else:
        path = select_command(scl_config)

    if path:
        # Allow specifying the basename (like ~/.shell-command-logs/echo/2022w11g_133650_63ff),
        # or either file (the *.log or the *.time). If a file with the extention is given, the extension is removed
        path = remove_extension(path)

        # replaay the command
        return replay_command(path, scl_config)
    else:
        return 1

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

