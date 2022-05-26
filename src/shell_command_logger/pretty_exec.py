#!/usr/bin/env python3
import argparse
import base64
from datetime import datetime, timezone
import getpass
import json
import platform
import subprocess
import sys
import traceback
from typing import Optional


# Since this scriptwill be called using something like `script [...] -c "./pretty_exec ARGUMENTS"` escaping arguments safely and correctly may be hard
# and mistakes could result is subtle bugs. So instead the arguments will be passed in a shell-safe format.
# My idea is to JSON encode the argv array and then base64 encode the resulting string
# @LINK: Opposite of simple_recorder.py:encode_command()
def decode_command(encoded_command_array: str) -> list[str]:
    command_json_bytes = base64.b64decode(encoded_command_array)
    command_json = command_json_bytes.decode("utf-8")
    command_list = json.loads(command_json)

    # Make sure, that the data really is a list of strings
    if type(command_list) == list:
        for item in command_list:
            if type(item) != str:
                break
        return command_list
    raise Exception(f"Expected json to contain a list of strings, but got '{command_json}'")


def write_json(path, json_data) -> None:
    try:
        with open(path, "w") as f:
            json.dump(json_data, f)
    except Exception:
        print(f"[shell-command-logger::error] Failed to write to file '{path}'")
        traceback.print_exc()


def current_timestamp() -> str:
    # Z means Zulu time (UTC)
    # Use timespec=seconds to hide the millisecond part
    return datetime.now(timezone.utc).isoformat("Z", timespec="seconds")
    # Can be parsed with datetime.fromisoformat


def execute_command(command: list[str]) -> tuple[int, Optional[str]]:
    try:
        status_code = subprocess.call(command)
        # Process war executed normally: return the status code without an error message
        return (status_code, None)
    except FileNotFoundError as e:
        error_message = f"Program '{command[0]}' not found"
        print(f"[shell-command-logger] {error_message}")
    except KeyboardInterrupt:
        error_message = "Interrupted by user (Ctrl-C / SIGINT)"
        print(f"\n[shell-command-logger] {error_message}")
    except Exception as e:
        try:
            # Exception type and message
            error_message = f"{type(e).__name__}: {e}"
        except Exception:
            # Fall back to only the message
            error_message = str(e)
        traceback.print_exc()

    # Executing the command failed due to an internal error.
    # Return -1 as status code and the error message
    return (-1, error_message)


def main(command: list[str], metadata_file: str) -> int:
    data: dict = {
        "command": command,
        "user": getpass.getuser(),
        "hostname": platform.node(),
        "start_time": current_timestamp() 
    }

    status_code, error_message = execute_command(command)

    data.update({
        "end_time": current_timestamp(),
        "error_message": error_message,
        "status_code": status_code,
    })

    write_json(metadata_file, data)

    return status_code


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("encoded_command", help="A base64 encoded JSON list containing the command to execute")
    ap.add_argument("metadata_file", help="the file to write the metadata to")
    args = ap.parse_args()

    command = decode_command(args.encoded_command)
    exit_code = main(command, args.metadata_file)
    sys.exit(exit_code)
