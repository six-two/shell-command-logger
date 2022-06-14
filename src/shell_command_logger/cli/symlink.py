import os
# import the code from this package
from shell_command_logger import print_color
from shell_command_logger.symlink import SYMLINK_MANAGER, update_symlinks
from shell_command_logger.config import load_config, sanitize_config

SUBCOMMAND_NAMES = ["sl", "symlinks"]
ARG_PARSER_OPTIONS = {
    "description": "This command can be used to manage symlinks, which can be used to automatcally log the output of specified binaries",
    "help": "manage symlinks",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    mutex = ap.add_mutually_exclusive_group()
    mutex.add_argument("-s", "--set", nargs="*", help="overwrites the alias list with the given values. This deletes all old entries")
    mutex.add_argument("-a", "--add", nargs="+", help="add the given programs to the alias list")
    mutex.add_argument("-d", "--delete", nargs="+", help="delete the given programs from the alias list")
    mutex.add_argument("--defaults", action="store_true", help="reset the alias list back to the default value")


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    if args.set is not None:
        with SYMLINK_MANAGER as programs_wrapper:
            programs_wrapper.list = args.set
    elif args.add:
        with SYMLINK_MANAGER as programs_wrapper:
            programs_wrapper.list += args.add
    elif args.delete:
        with SYMLINK_MANAGER as programs_wrapper:
            programs_wrapper.list = [x for x in programs_wrapper.list if x not in args.delete]
    elif args.defaults:
        try:
            os.remove(SYMLINK_MANAGER.state_file)
        except Exception:
            print_color(f"Failed to remove current list file: '{SYMLINK_MANAGER.state_file}'", "red")
    else:
        for program in SYMLINK_MANAGER.get_read_only_list():
            print(program)
    
    # Whatever we do, make sure that the symlinks are up to date
    scl_config = sanitize_config(load_config())
    update_symlinks(scl_config, SYMLINK_MANAGER.get_read_only_list())

    # @TODO check somewhere that symlink folder is first entry in PATH

    # By default return 0 (success)
    return 0
