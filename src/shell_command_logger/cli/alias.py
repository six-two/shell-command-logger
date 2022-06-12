import os
# import the code from this package
from shell_command_logger import print_color
from shell_command_logger.alias import ALIAS_MANAGER, print_text_to_source

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
    mutex.add_argument("--reset", "--defaults", action="store_true", help="reset the alias list back to the default value")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    if args.print:
        shell = args.print
        print_text_to_source(shell)
    elif args.set is not None:
        with ALIAS_MANAGER as programs_wrapper:
            programs_wrapper.list = args.set
    elif args.add:
        with ALIAS_MANAGER as programs_wrapper:
            programs_wrapper.list += args.add
    elif args.delete:
        with ALIAS_MANAGER as programs_wrapper:
            programs_wrapper.list = [x for x in programs_wrapper.list if x not in args.delete]
    elif args.reset:
        try:
            os.remove(ALIAS_MANAGER.state_file)
        except Exception:
            print_color(f"Failed to remove current list file: '{ALIAS_MANAGER.state_file}'", "red")
    else:
        for program in ALIAS_MANAGER.get_read_only_list():
            print(program)

    # By default return 0 (success)
    return 0
