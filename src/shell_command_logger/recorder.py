#!/usr/bin/env python3
import base64
import json
import os
import subprocess
import sys
import time
import secrets

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
    encoded_command = encode_command(command_and_arguments)
    pretty_exec = os.path.join(REAL_SCRIPT_DIR, "pretty_exec.py")

    script_command = [
        "script",
        "--log-out", f"{output_file}.log", # stores the output
        "--log-timing", f"{output_file}.time", # also stores the timing, so that the output can be played back to watch when what happened
        "--command", f"python3 {pretty_exec} {encoded_command}", # runs our command, which displays the command, timestamp, exit code, etc
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


def main_recorder(command: list[str], calling_scripts__file__value: str) -> int:
    # The name the file was called as (for example `rec` if `/tmp/rec` is a symlink to this script)
    used_binary_name = os.path.basename(calling_scripts__file__value)
    # The original scripts file name (for example simple_recorder.py if `/tmp/rec` is a symlink to this script)
    real_binary_name = os.path.basename(os.path.realpath(calling_scripts__file__value))

    # When the script is an alias (symlink), use the symlink name as the command to execute
    # To test this you can for example:
    # 1) ln -s ./simple_recorder.py /tmp/ls
    # 2) Call it via the symlink: /tmp/ls -1 /
    if used_binary_name != real_binary_name:
        command = [used_binary_name, *command]

    # print("Debug", command)
    if not command:
        print("Usage: <command> [arguments...]")
        print("Example: ls -1 '/home/johndoe/My Documents/'")
        return 1

    command_name = os.path.basename(command[0])
    output_dir = os.path.join(OUTPUT_PATH, command_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, get_timestamp_filename())

    exit_code = record_command(command, output_file)
    return exit_code


if __name__ == "__main__":
    command = sys.argv[1:]
    exit_code = main_recorder(command, __file__)
    sys.exit(exit_code)

