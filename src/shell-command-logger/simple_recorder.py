#!/usr/bin/env python3
import base64
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


# @LINK: Opposite of pretty_exec.py:decode_command()
def encode_command(command_and_arguments: str) -> str:
    command_json = json.dumps(command_and_arguments)
    command_json_bytes = command_json.encode("utf-8")
    encoded_command = base64.b64encode(command_json_bytes)
    return encoded_command.decode("utf-8")


def record_command(command_and_arguments: list[str], output_file: str) -> int:
    encoded_command = encode_command(command_and_arguments)
    pretty_exec = os.path.join(SCRIPT_DIR, "pretty_exec.py")
    timing_file = f"{output_file}.time"

    script_command = ["script",
        "--log-out", output_file, # stores the output
        "--log-timing", timing_file, # also stores the timing, so that the output can be played back to watch when what happened
        "--command", f"{pretty_exec} {encoded_command}", # runs our command, which displays the command, timestamp, exit code, etc
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


if __name__ == "__main__":
    command = sys.argv[1:]
    if not command:
        print("Usage: <command> [arguments...]")
        print("Example: ls -1 '/home/johndoe/My Documents/'")
        sys.exit(1)
    exit_code = record_command(command, "/tmp/simple_recorder")
    sys.exit(exit_code)

