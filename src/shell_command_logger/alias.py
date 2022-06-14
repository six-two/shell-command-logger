import os
import shlex
import shutil
import sys
# local files
from shell_command_logger.list_manager import ListManager
from shell_command_logger.symlink import get_binary_name_or_path

_CONFIG_FILE = os.path.expanduser("~/.config/shell-command-logger/aliases.txt")
_DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "default_aliases.txt")


def check_program_name(program: str) -> None:
    if len(program.split()) > 1:
        raise Exception(f"Program name '{program}' contains whitespaces")
    if not shutil.which(program):
        raise Exception(f"Program '{program}' is not installed")


def shell_alias(shell: str, program: str) -> str:
    # This allows to use aliases, even if 'scl' is not in $PATH
    scl = shlex.quote(get_binary_name_or_path())

    if shell in ["bash", "fish", "zsh"]:
        return f"alias {program}=\"{scl} log {program}\""
    else:
        raise ValueError(f"Unknown shell '{shell}'. Supported are bash, fish and zsh")


def print_text_to_source(shell: str) -> None:
    """
    Return the text that contains the alias commands for the given shell.
    The result should be passed to `source`.
    """
    for program in ALIAS_MANAGER.get_read_only_list():
        try:
            check_program_name(program)
            print(shell_alias(shell, program))
        except Exception as ex:
            # Print to stderr so that this will not be sourced but instea shown to the user
            print(f"Error creating alias for '{program}':", ex, file=sys.stderr)



ALIAS_MANAGER = ListManager(_CONFIG_FILE, _DEFAULT_CONFIG_FILE) 
