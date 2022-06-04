#!/usr/bin/env python3
import argparse
import os
import sys
# import the code from this package
from shell_command_logger.search import get_all_searchable_commands
from shell_command_logger.config import load_config, sanitize_config

SUBCOMMAND_NAMES = ["s", "search"]
ARG_PARSER_OPTIONS = {
    "description": "This command can be used to search the logged commands",
    "help": "search logs",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    mutex_status = ap.add_mutually_exclusive_group()
    mutex_status.add_argument("-s", "--status-code", type=int, help="only show results with the given status code. Programs terminated by internal errors have status code -1")
    mutex_status.add_argument("-S", "--exclude-status-code", type=int, help="exclude results with the given status code. Programs terminated by internal errors have status code -1")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    scl_config = sanitize_config(load_config())
    search_results = get_all_searchable_commands(scl_config)

    print(args.status_code, args.exclude_status_code)
    if args.status_code != None:
        search_results = [x for x in search_results if x.metadata.status_code == args.status_code]
    elif args.exclude_status_code != None:
        search_results = [x for x in search_results if x.metadata.status_code != args.exclude_status_code]

    for result in search_results:
        print(result.file_path)

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

