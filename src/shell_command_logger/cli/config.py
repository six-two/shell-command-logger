import os
# import the code from this package
from shell_command_logger import print_color
from shell_command_logger.config import load_config, sanitize_config, SclConfig, config_to_parser, save_parser_as_config, parser_to_text, DEFAULT_CONFIG, CONFIG_FILE, _KEY_SECTION


SUBCOMMAND_NAMES = ["c", "config"]
ARG_PARSER_OPTIONS = {
    "description": f"This subcommand can be used to view or modify the config file. You can also manually modify the config file located at {CONFIG_FILE}.",
    "help": "view and modify config",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    mutex = ap.add_mutually_exclusive_group()
    mutex.add_argument("-d", "--defaults", action="store_true", help="reset all settings back to the defaults")
    mutex.add_argument("-g", "--get", metavar="<key>", help="get the value of <key>")
    mutex.add_argument("-s", "--set", metavar=("<key>", "<new_value>"), nargs=2, help="set an option: <key> = <new_value>")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    scl_config = load_config()

    if args.set:
        key, new_value = args.set
        parser = config_to_parser(scl_config)
        parser[_KEY_SECTION][key] = new_value
        save_parser_as_config(parser)
    elif args.get:
        key = args.get
        parser = config_to_parser(scl_config)
        try:
            print(parser[_KEY_SECTION][key])
        except KeyError:
            print(f"The value '{key}' does not exist!")
            return 1
    elif args.defaults:
        parser = config_to_parser(DEFAULT_CONFIG)
        save_parser_as_config(parser)
    else:
        # By default print out the current config
        parser = config_to_parser(scl_config)
        text = parser_to_text(parser)
        print(text.rstrip())

    try:
        sanitize_config(load_config())
        return 0
    except Exception as ex:
        print_color(f"Error validating config: {ex}", "red", bold=True)
        return 1
    # By default return 0 (success)
