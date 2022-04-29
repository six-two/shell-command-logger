import os
import shutil
import sys

SCL_COMMAND = "scl"
CONFIG_FILE = os.path.expanduser("~/.config/shell-command-logger/aliases.txt")
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "default_aliases.txt")


def check_program_name(program: str) -> None:
    if len(program.split()) > 1:
        raise Exception(f"Program name '{program}' contains whitespaces")
    if not shutil.which(program):
        raise Exception(f"Program '{program}' is not installed")


def shell_alias(shell: str, program: str) -> str:
    if shell in ["bash", "fish", "zsh"]:
        return f"alias {program}='{SCL_COMMAND} {program}'"
    else:
        raise ValueError(f"Unknown shell '{shell}'. Supported are bash, fish and zsh")


def load_alias_file() -> list[str]:
    if not os.path.exists(CONFIG_FILE):
        # Copy my defaults file over
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        shutil.copyfile(DEFAULT_CONFIG_FILE, CONFIG_FILE)

    with open(CONFIG_FILE, "r") as f:
        lines = f.read().split("\n")
    # Remove leading/trailing whitespace and empty lines
    return [x.strip() for x in lines if x.strip()]


def save_alias_file(aliases: list[str]) -> None:
    # remove duplicates
    aliases = list(set(aliases))
    lines = [f"{x}\n" for x in sorted(aliases)]

    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write("".join(lines))


def print_text_to_source(shell: str) -> None:
    for program in load_alias_file():
        try:
            check_program_name(program)
            print(shell_alias(shell, program))
        except Exception as ex:
            # Print to stderr so that this will not be sourced but instea shown to the user
            print(f"Error creating alias for '{program}':", ex, file=sys.stderr)

