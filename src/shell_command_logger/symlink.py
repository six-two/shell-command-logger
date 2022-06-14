import logging
import os
import shutil
# local files
from shell_command_logger import print_error
from shell_command_logger.list_manager import ListManager
from shell_command_logger.main_file import create_symlink_to_main_file
from shell_command_logger.config import SclConfig

_CONFIG_FILE = os.path.expanduser("~/.config/shell-command-logger/symlinks.txt")
_DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "default_symlinks.txt")


def check_program_name(program: str) -> None:
    if len(program.split()) > 1:
        raise Exception(f"Program name '{program}' contains whitespaces")
    if not shutil.which(program):
        raise Exception(f"Program '{program}' is not installed")


def update_symlinks(scl_config: SclConfig, programs_to_symlink: list[str]) -> None:
    # First remove bad files
    for file_name in os.listdir(scl_config.symlink_dir):
        if file_name not in programs_to_symlink:
            # This is a program we should not symlink to
            path = os.path.join(scl_config.symlink_dir, file_name)
            logging.debug(f"Removing file from symlink folder: {path}")
            try:
                os.remove(path)
            except Exception:
                print_error(f"Failed to delete file: {path}")
    
    # Then make sure we have correct symlinks for every requested program
    for program in programs_to_symlink:
        path = os.path.join(scl_config.symlink_dir, program)
        create_symlink_to_main_file(path)


SYMLINK_MANAGER = ListManager(_CONFIG_FILE, _DEFAULT_CONFIG_FILE) 
