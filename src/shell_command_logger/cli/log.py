#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Optional
# import the code from this package
from shell_command_logger.recorder import get_command_path, get_timestamp_filename, record_command
from shell_command_logger.config import load_config, sanitize_config, SclConfig


SUBCOMMAND_NAMES = ["l", "log"]
ARG_PARSER_OPTIONS = {
    "description": "Run the given command and log the results",
    "help": "record a command",
}

__SCRIPT_FILE = None

def set_script_file(calling_scripts__file__value: str) -> None:
    global __SCRIPT_FILE
    __SCRIPT_FILE = calling_scripts__file__value


def get_name_when_called_by_symlink() -> Optional[str]:
    """
    When this script was called by a symlink, return the symlink's file name (unless it is exactly the name of this program).
    Otherwise return None.
    """
    calling_scripts__file__value = get_script_file()
    # The name the file was called as (for example `rec` if `/tmp/rec` is a symlink to this script)
    used_binary_name = os.path.basename(calling_scripts__file__value)
    # The original scripts file name (for example simple_recorder.py if `/tmp/rec` is a symlink to this script)
    real_binary_name = os.path.basename(os.path.realpath(calling_scripts__file__value))

    if used_binary_name == real_binary_name:
        # Called normally or symlinked but symlink has same name -> return None
        return None
    else:
        # Return the name this script was called by
        return used_binary_name


def get_script_file() -> str:
    if not __SCRIPT_FILE:
        raise Exception("script file is not set")
    return __SCRIPT_FILE


def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    ap.add_argument("command", nargs=argparse.REMAINDER, help="the command to execute (required)")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    command = list(args.command)
    if not command:
        print("You need to specify a command to log. Use option --help for more details")
        return 1
    else:
        return _record_command(command)


def record_command_when_called_by_symlink(symlink_name: str, argv: list[str]) -> int:
    return _record_command([symlink_name, *argv])


def _record_command(command: list[str]):
    scl_config = load_config()
    scl_config = sanitize_config(scl_config)

    # make sure, that we do not call our own script recursively
    command[0] = get_command_path(command[0], get_script_file())

    command_name = os.path.basename(command[0])
    output_dir = os.path.join(scl_config.output_dir, command_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, get_timestamp_filename())

    exit_code = record_command(command, output_file)
    return exit_code


def _main():
    # Parse arguments
    ap = argparse.ArgumentParser()
    populate_agrument_parser(ap)
    args = ap.parse_args()

    # Run the main function
    exit_code = subcommand_main(args)

    # And exit
    sys.exit(exit_code)

if __name__ == "__main__":
    _main()

