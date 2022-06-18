import argparse
import sys
from typing import Callable
# import the code from this package
import shell_command_logger
from shell_command_logger import print_color
from shell_command_logger.backports import TimeParseException
from shell_command_logger.config import InvalidConfigException
from shell_command_logger.cli import alias, check, config, log, replay, search, symlink
from shell_command_logger.main_file import set_python_main_file
from shell_command_logger.debug import init_debugging
# local files
from ..backports import Dict

class SubcommandHandlerException(Exception):
    pass

class SubcommandHandler:
    def __init__(self, argument_parser, subcommand_variable_name: str = "subcommand", subcommand_required: bool = False) -> None:
        self.ap = argument_parser
        self.subcommand_variable_name = subcommand_variable_name
        self.ap_subparsers = self.ap.add_subparsers(metavar="SUBCOMMAND", required=subcommand_required, dest=subcommand_variable_name)
        # Maps from subcommand names to the coresponding main functions
        self.main_function_map: Dict[str, Callable] = {}

    def register_module(self, module) -> None:
        for name in module.SUBCOMMAND_NAMES:
            ap_module = self.ap_subparsers.add_parser(name, **module.ARG_PARSER_OPTIONS)
            module.populate_agrument_parser(ap_module)

            if name in self.main_function_map:
                raise SubcommandHandlerException(f"The subcommand '{name}' is specified twice")

            self.main_function_map[name] = module.subcommand_main

    def subcommand_main(self, args) -> int:
        subcommand_name = getattr(args, self.subcommand_variable_name)
        if not subcommand_name:
            # If no subcommand is specified, we show the help
            self.ap.print_help()
            return 1

        fn_main = self.main_function_map.get(subcommand_name)
        if fn_main:
            return fn_main(args)
        else:
            raise SubcommandHandlerException(f"No subcommand with name '{subcommand_name}' registered")


def main(main_python_file: str) -> None:
    # Register the calling binaries path
    set_python_main_file(main_python_file)
    if symlink_name := shell_command_logger.cli.log.get_name_when_called_by_symlink():
        exit_code = shell_command_logger.cli.log.record_command_when_called_by_symlink(symlink_name, sys.argv[1:])
        sys.exit(exit_code)

    # Setting up argument parser
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="The shell-command-logger (scl) allows you to record commands. Afterwards the recorded commands can be replay and searched.",
        epilog=f"Installed version: {shell_command_logger.get_version_string()}\nDocumentation: https://shell-command-logger.six-two.dev/"
    )
    ap.add_argument("-V", "--version", action="version", version=shell_command_logger.get_version_string())
    ap.add_argument("-d", "--debug", action="store_true", help="print debugging information")
    handler = SubcommandHandler(ap)

    for module in [alias, check, config, log, replay, search, symlink]:
        handler.register_module(module)

    # Run the selected submodule
    args = ap.parse_args()

    if args.debug:
        init_debugging(True)

    try:
        exit_code = handler.subcommand_main(args)
    except InvalidConfigException as ex:
        print_color("Your configuration is not valid:", "red", bold=True)
        print_color(str(ex), "red", bold=True)
        print_color("Hint: You can use 'scl config --defaults' to reset your configuration to the defaults", "yellow")
        exit_code = 1
    except TimeParseException as ex:
        print_color(str(ex), "red", bold=True)
        exit_code = 1
  
    sys.exit(exit_code)

