#!/usr/bin/env python3
import argparse
import os
import sys
# import the code from this package
from shell_command_logger.replay import select_file, select_command, remove_extension, replay_command
from shell_command_logger.config import load_config, sanitize_config, SclConfig, config_to_parser, save_parser_as_config, parser_to_text, DEFAULT_CONFIG


SUBCOMMAND_NAMES = ["c", "config"]
ARG_PARSER_OPTIONS = {
    "description": "This subcommand can be used to view or modify the config of scl and sclm",
    "help": "view and modify config",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    mutex = ap.add_mutually_exclusive_group()
    mutex.add_argument("-d", "--defaults", action="store_true", help="reset all settings back to the defaults")
    mutex.add_argument("-g", "--get", metavar=("<section>", "<key>",), nargs=2, help="get the value of <section>.<key>")
    mutex.add_argument("-s", "--set", metavar=("<section>", "<key>", "<new_value>"), nargs=3, help="set an option: <section>.<key> = <new_value>")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    scl_config = load_config()

    if args.set:
        section, key, new_value = args.set
        parser = config_to_parser(scl_config)
        parser[section][key] = new_value
        save_parser_as_config(parser)
    elif args.get:
        section, key = args.get
        parser = config_to_parser(scl_config)
        try:
            print(parser[section][key])
        except KeyError:
            print(f"The value '{section}.{key}' does not exist!")
            return 1
    elif args.defaults:
        parser = config_to_parser(DEFAULT_CONFIG)
        save_parser_as_config(parser)
    else:
        # By default print out the current config
        parser = config_to_parser(scl_config)
        text = parser_to_text(parser)
        print(text.rstrip())

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

