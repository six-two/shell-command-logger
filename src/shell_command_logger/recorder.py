#!/usr/bin/env python3
import base64
import json
import os
import subprocess
import shlex
import sys
import time
import secrets
# local
from . import get_version_string
from .config import load_config, sanitize_config

# This also works when the file is a symlink (gets the original dir)
REAL_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


# @TODO load settings from a file.
# Optional: first try ~/.config/shell-command-logger/config.yaml, then /etc/shell-command-logger/config.yaml
OUTPUT_PATH = os.path.expanduser("~/.shell-command-logs/")
RANDOM_BYTES_IN_FILE_NAME = 2


# @LINK: Opposite of pretty_exec.py:decode_command()
def encode_command(command_and_arguments: str) -> str:
    command_json = json.dumps(command_and_arguments)
    command_json_bytes = command_json.encode("utf-8")
    encoded_command = base64.b64encode(command_json_bytes)
    return encoded_command.decode("utf-8")


def record_command(command_and_arguments: list[str], output_file: str) -> int:
    pretty_exec = os.path.join(REAL_SCRIPT_DIR, "pretty_exec.py")
    encoded_command = encode_command(command_and_arguments)
    inner_command = ["python3", pretty_exec, encoded_command, f"{output_file}.json"]

    script_command = [
        "script",
        "--log-out", f"{output_file}.log", # stores the output
        "--log-timing", f"{output_file}.time", # also stores the timing, so that the output can be played back to watch when what happened
        "--command", shlex.join(inner_command), # runs our command, which displays the command, timestamp, exit code, etc
        "--return", # return exit code of the child process
        "--output-limit", "1g", # If the output is larger than one Gigabyte, something probably went wrong.
        # This prevents your harddrive from overflowing. @TODO: add a flag/option to disable this
        "--quiet", # Hide the "Script started/stopped" messages
    ]

    try:
        exit_code = subprocess.call(script_command)
        return exit_code
    except KeyboardInterrupt:
        return 2


def get_timestamp_filename() -> str:
    now = time.gmtime()
    date = time.strftime("%Gw%V")
    day = "abcdefg"[now.tm_wday] # Monday -> a, ..., Sunday -> g
    time_str = time.strftime("%H%M%S")
    random = secrets.token_hex(RANDOM_BYTES_IN_FILE_NAME) # a random value to (with a high likelyhood) prevent mutiple logs started in the same second from overwriting each other.
    # Not perfect, but prevents having to implement a locking / consensus system

    timestamp = f"{date}{day}_{time_str}_{random}"
    return timestamp


def get_command_path(command_name: str, calling_scripts__file__value: str) -> str:
    """
    Gets the full path for a programm name, but will ignore symlinks to this script.
    This prevents recursive calls to this script
    """
    if "/" in command_name:
        # the command is a path to a file, so the $PATH is not used
        return command_name
    else:
        # Resolve a command to a full path, just in case there is a symlink to this script in the $PATH
        path = os.getenv('PATH')
        for p in path.split(os.path.pathsep):
            p = os.path.join(p, command_name)
            if os.path.exists(p) and os.access(p,os.X_OK):
                if not os.path.samefile(p, calling_scripts__file__value):
                    return p
        # Maybe it is a shell builtin? Just return the original value
        return command_name
        # raise Exception(f"No binary found for '{command_name}', that is not a link to this script")


def main_recorder(command: list[str], calling_scripts__file__value: str) -> int:
    # The name the file was called as (for example `rec` if `/tmp/rec` is a symlink to this script)
    used_binary_name = os.path.basename(calling_scripts__file__value)
    # The original scripts file name (for example simple_recorder.py if `/tmp/rec` is a symlink to this script)
    real_binary_name = os.path.basename(os.path.realpath(calling_scripts__file__value))

    scl_config = load_config()
    scl_config = sanitize_config(scl_config)

    # When the script is an alias (symlink), use the symlink name as the command to execute
    # To test this you can for example:
    # 1) ln -s ./simple_recorder.py /tmp/ls
    # 2) Call it via the symlink: /tmp/ls -1 /
    if used_binary_name != real_binary_name:
        command = [used_binary_name, *command]

    if not command:
        print("This script logs the output of a command, so that it can later be used by scripts like scl-replay\n")
        print("Usage: <command> [arguments...]")
        print("Example arguments: ls -1 '/home/johndoe/My Documents/'")
        print("Version:", get_version_string())
        return 1

    # make sure, that we do not call our own script recursively
    command[0] = get_command_path(command[0], calling_scripts__file__value)


    command_name = os.path.basename(command[0])
    output_dir = os.path.join(scl_config.output_dir, command_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, get_timestamp_filename())

    exit_code = record_command(command, output_file)
    return exit_code


if __name__ == "__main__":
    command = sys.argv[1:]
    exit_code = main_recorder(command, __file__)
    sys.exit(exit_code)

