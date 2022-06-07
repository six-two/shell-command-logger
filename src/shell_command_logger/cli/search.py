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
    mutex_status.add_argument("-s", "--status-codes", nargs="+", type=int, help="only show results with one of the given status codes. Programs terminated by internal errors have status code -1")
    mutex_status.add_argument("-S", "--exclude-status-codes", nargs="+", type=int, help="exclude results with one of the given status codes. Programs terminated by internal errors have status code -1")

    mutex_user = ap.add_mutually_exclusive_group()
    mutex_user.add_argument("-u", "--users", nargs="+", help="only show commands run by one of the given users")
    mutex_user.add_argument("-U", "--exclude-users", nargs="+", help="exclude commands run by any of the given users")

    mutex_hostname = ap.add_mutually_exclusive_group()
    mutex_hostname.add_argument("--hosts", nargs="+", help="only show commands run on one of the given hosts")
    mutex_hostname.add_argument("-H", "--exclude-hosts", nargs="+", help="exclude commands executed on one of the given hosts")

    mutex_error = ap.add_mutually_exclusive_group()
    mutex_error.add_argument("-e", "--errors", nargs="*", help="only show commands that contain one of the given texts in their error message. No argument will match any command with errors")
    mutex_error.add_argument("-E", "--exclude-errors", nargs="*", help="exclude commands that contain one of the given texts in their error message. No argument will match any command with errors")

    mutex_command = ap.add_mutually_exclusive_group()
    mutex_command.add_argument("-c", "--commands", nargs="+", help="only show commands that contain at least one of the given strings in one of its arguments")
    mutex_command.add_argument("-C", "--exclude-commands", nargs="+", help="exclude commands that contain the any of the given strings in one of its arguments")

    mutex_time = ap.add_mutually_exclusive_group()
    mutex_time.add_argument("-d", "--days", nargs="+", help="show commands that were running on one of the given days (in UTC)")
    mutex_time.add_argument("-D", "--exclude-days", nargs="+", help="exclude commands that were running on one of the given days (in UTC)")

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
    is_match_status_code = lambda metadata, value_list: metadata.status_code in value_list
    search_results = filter_by_metadata(search_results, args.status_codes, args.exclude_status_codes, is_match_status_code)
    
    # Filter by username
    is_match_user = lambda metadata, value_list: metadata.user in value_list
    search_results = filter_by_metadata(search_results, args.users, args.exclude_users, is_match_user)

    # Filter by hostname
    is_match_host = lambda metadata, value_list: metadata.hostname in value_list
    search_results = filter_by_metadata(search_results, args.hosts, args.exclude_hosts, is_match_host)

    # Filter by error message
    def is_match_error(metadata: Metadata, value_list: list[str]) -> bool:
        if metadata.error_message:
            if value_list == []:
                # No values -> matches any error
                return True
            else:
                # Check if any value is a substring of error_message
                for value in value_list:
                    if value in metadata.error_message:
                        # At loast one match found
                        return True
                # No matches found
                return False
        else:
            # If no error message exists, it can not match
            return False
    search_results = filter_by_metadata(search_results, args.errors, args.exclude_errors, is_match_error)

    # Filter by command
    def is_match_command(metadata: Metadata, value_list: list[str]) -> bool:
        for value in value_list:
            for arg in metadata.command:
                # Test if ant value is a substring of any argument
                if value in arg:
                    return True
        return False
    search_results = filter_by_metadata(search_results, args.commands, args.exclude_commands, is_match_command)

    if args.days or args.exclude_days:
        # Only parse the dates once, this makes it necessary to first parse the dates and then define a function that uses the results
        date_checker = DateChecker(args.days or args.exclude_days)
        is_match_day = lambda metadata, _: date_checker.is_match(metadata)

        search_results = filter_by_metadata(search_results, args.days, args.exclude_days, is_match_day)


    for result in search_results:
        print(result.file_path)

    # By default return 0 (success)
    return 0


class DateChecker:
    def __init__(self, date_list: list[str]) -> None:
        self.boundaries: tuple[datetime, datetime] = []
        for date_string in date_list:
            parsed = parse_datetime_string(date_string)

            # First second of the day
            start = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            # Last second of the day
            end = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)

            self.boundaries.append((start, end))
        print("dbg:datechecker", self.boundaries)
        # @TODO:BUG parsed date is off by one
        # $ scl s -d 'June 8'
        # dbg:datechecker [(datetime.datetime(2022, 6, 7, 0, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2022, 6, 7, 23, 59, 59, 999999, tzinfo=datetime.timezone.utc))]

    def is_match(self, metadata: Metadata) -> bool:
        for start, end in self.boundaries:
            if is_running_during_timeframe(metadata, start, end):
                return True
        return False

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

