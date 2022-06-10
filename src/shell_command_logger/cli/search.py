from datetime import datetime
import os
import subprocess
from typing import Any, Callable
# import the code from this package
from shell_command_logger.search import get_all_searchable_commands, SearchableCommand, Metadata, is_running_during_timeframe, get_command_output
from shell_command_logger.config import load_config, sanitize_config
from shell_command_logger.backports import parse_datetime_string
from shell_command_logger.replay import remove_extension, format_command_builder, select_formatted, replay_command

SUBCOMMAND_NAMES = ["s", "search"]
ARG_PARSER_OPTIONS = {
    "description": "This command can be used to search the logged commands",
    "help": "search logs",
}

def create_only_or_exclude_filter(ap, short_flag: str, long_flag: str, description: str, **kwargs) -> None:
    """
    An helper method to reduce redundant code and thus reduce copy paste errors
    """
    if len(short_flag) != 1:
        raise Exception("short_flag needs to be a single character")
    
    # The only X and the exclude X options are mutually exclusive
    mutex = ap.add_mutually_exclusive_group()
    # The only show X flag
    mutex.add_argument(
        f"-{short_flag.lower()}",
        f"--{long_flag}",
        nargs="+",
        help=f"only show commands {description}",
        **kwargs,
    )
    # The exclude X flag
    mutex.add_argument(
        f"-{short_flag.upper()}",
        f"--exclude-{long_flag}",
        nargs="+",
        help=f"exclude commands {description}",
        **kwargs,
    )


def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    create_only_or_exclude_filter(ap, "s", "status-codes", "with one of the given status codes. Programs terminated by internal errors have status code -1", type=int)
    create_only_or_exclude_filter(ap, "u", "users", "run by one of the given users")

    mutex_hostname = ap.add_mutually_exclusive_group()
    # -h is already taken by --help
    mutex_hostname.add_argument("--hosts", nargs="+", help="only show commands run on one of the given hosts")
    mutex_hostname.add_argument("-H", "--exclude-hosts", nargs="+", help="exclude commands executed on one of the given hosts")

    create_only_or_exclude_filter(ap, "e", "errors", "that contain one of the given texts in their error message. No argument will match any command with errors")
    create_only_or_exclude_filter(ap, "p", "program", "that match one of the given program names")
    create_only_or_exclude_filter(ap, "a", "arguments", "that contain at least one of the given strings in one of its arguments")
    create_only_or_exclude_filter(ap, "d", "days", "that were running on one of the given days (in UTC)")

    ap.add_argument("-g", "--grep-output", metavar=("PATTERN_AND_FLAGS"), help="only show commands, if `echo <COMMAND_OUTPUT> | grep <PATTERN_AND_FLAGS>` returns the status code 0. Generally this means, that matches were found")

    # TODO: start/end x before/after
    # TODO: runtime longer/shorter than

    # These arguments specify what to do with the results
    # TODO -o
    mutex_action = ap.add_mutually_exclusive_group()
    mutex_action.add_argument("-r", "--replay", action="store_true", help="interactively select one of the search results to replay")

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

    # Filter by program
    def is_match_program(metadata: Metadata, value_list: list[str]) -> bool:
        program_name = os.path.basename(metadata.command[0])
        return program_name in value_list
    search_results = filter_by_metadata(search_results, args.program, args.exclude_program, is_match_program)

    # Filter by command arguments
    def is_match_command(metadata: Metadata, value_list: list[str]) -> bool:
        for value in value_list:
            for arg in metadata.command[1:]:
                # Test if ant value is a substring of any argument
                if value in arg:
                    return True
        return False
    search_results = filter_by_metadata(search_results, args.arguments, args.exclude_arguments, is_match_command)

    if args.days or args.exclude_days:
        # Only parse the dates once, this makes it necessary to first parse the dates and then define a function that uses the results
        date_checker = DateChecker(args.days or args.exclude_days)
        is_match_day = lambda metadata, _: date_checker.is_match(metadata)

        search_results = filter_by_metadata(search_results, args.days, args.exclude_days, is_match_day)


    if args.grep_output:
        search_results = filter_by_grep(search_results, args.grep_output)

    if args.replay:
        file_names = [x.file_path for x in search_results]
        format_function = format_command_builder(scl_config)
        path = select_formatted(scl_config, format_function, file_names)
        if path:
            replay_command(path, scl_config)
    else:
        for result in search_results:
            print(result.file_path)

    # By default return 0 (success)
    return 0


def filter_by_grep(entries: list[SearchableCommand], arguments_and_pattern: str) -> list[SearchableCommand]:
    grep_command = f"grep {arguments_and_pattern}"
    matches = []
    for entry in entries:
        log_file_name = remove_extension(entry.file_path) + ".log" # Access the .log file which contains the output
        command_output = get_command_output(log_file_name)

        # pipe the command output into grep
        result = subprocess.run(grep_command, shell=True, input=command_output, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=2)
        # Accept result if grep returned with code 0 (results found)
        if result.returncode == 0:
            matches.append(entry)
    
    return matches


class DateChecker:
    def __init__(self, date_list: list[str]) -> None:
        self.boundaries: list[tuple[datetime, datetime]] = []
        for date_string in date_list:
            parsed = parse_datetime_string(date_string)

            # First second of the day
            start = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            # Last second of the day
            end = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)

            self.boundaries.append((start, end))

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
