#!/usr/bin/env python3
import argparse
from datetime import datetime
import os
import sys
from typing import Any, Callable
# import the code from this package
from shell_command_logger.search import get_all_searchable_commands, SearchableCommand, Metadata, is_running_during_timeframe
from shell_command_logger.config import load_config, sanitize_config
from shell_command_logger.backports import parse_datetime_string, round_up_date

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

    mutex_user = ap.add_mutually_exclusive_group()
    mutex_user.add_argument("-u", "--user", help="only show commands run by the given user")
    mutex_user.add_argument("-U", "--exclude-user", help="exclude commands run by the given user")

    mutex_hostname = ap.add_mutually_exclusive_group()
    mutex_hostname.add_argument("--host", help="only show commands run on the given host")
    mutex_hostname.add_argument("-H", "--exclude-host", help="exclude commands on the given host")

    mutex_error = ap.add_mutually_exclusive_group()
    # No flag -> None | Flag without value -> "" | Flag with value -> value
    mutex_error.add_argument("-e", "--error", nargs="?", const="", help="only show commands that have an error message. If an value is given, it has to be contained in the error message")
    mutex_error.add_argument("-E", "--exclude-error", nargs="?", const="", help="exclude commands that have an error message. If a value is given, only commands containing that string in their error message are excluded")

    mutex_command = ap.add_mutually_exclusive_group()
    mutex_command.add_argument("-c", "--command", help="only show commands that contain the given string in one of its arguments")
    mutex_command.add_argument("-C", "--exclude-command", help="exclude commands that contain the given string in one of its arguments")

    mutex_time = ap.add_mutually_exclusive_group()
    mutex_time.add_argument("-d", "--day", help="show commands that were running on the given day (in UTC)")

    # TODO: start/end x before/after
    # TODO: runtime longer/shorter than

def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    scl_config = sanitize_config(load_config())
    search_results = get_all_searchable_commands(scl_config)

    # Filter by status code
    is_match_status_code = lambda metadata, value: metadata.status_code == value
    search_results = filter_by_metadata(search_results, args.status_code, args.exclude_status_code, is_match_status_code)
    
    # Filter by username
    is_match_user = lambda metadata, value: metadata.user == value
    search_results = filter_by_metadata(search_results, args.user, args.exclude_user, is_match_user)

    # Filter by hostname
    is_match_host = lambda metadata, value: metadata.hostname == value
    search_results = filter_by_metadata(search_results, args.host, args.exclude_host, is_match_host)

    # Filter by error message
    is_match_error = lambda metadata, value: metadata.error_message and value in metadata.error_message
    search_results = filter_by_metadata(search_results, args.error, args.exclude_error, is_match_error)

    # Filter by command
    def is_match_command(metadata: Metadata, value: str) -> bool:
        for arg in metadata.command:
            if value in arg:
                return True
        return False
    search_results = filter_by_metadata(search_results, args.command, args.exclude_command, is_match_command)

    if args.day:
        parsed = parse_datetime_string(args.day)

        # First second of the day
        start = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
        # Last second of the day
        end = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)
        # Filter results
        search_results = [x for x in search_results if is_running_during_timeframe(x.metadata, start, end)]

    for result in search_results:
        print(result.file_path)

    # By default return 0 (success)
    return 0

def filter_by_metadata(entries: list[SearchableCommand], value: Any, exclude_value: Any, is_match: Callable[[Metadata, Any], bool]) -> list[SearchableCommand]:
    if value != None:
        if exclude_value != None:
            raise Exception("Both value and exclude_value have been supplied")
        return [x for x in entries if is_match(x.metadata, value)]
    elif exclude_value != None:
        return [x for x in entries if not is_match(x.metadata, exclude_value)]
    else:
        return entries


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

