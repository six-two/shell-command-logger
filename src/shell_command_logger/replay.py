#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
import sys
import traceback
from typing import Optional
# pip dependency
from termcolor import cprint
# local
from . import get_version_string

EXTENSIONS = [".json", ".log", ".time"]


def replay_command(output_file: str) -> int:
    metadata = parse_metadata(f"{output_file}.json")
    
    metadata and print_header(metadata)

    script_command = [
        "scriptreplay",
        "--log-out", f"{output_file}.log", # read the output file
        "--log-timing", f"{output_file}.time", # also read the timing file
        # @TODO: --divisor <num>     speed up or slow down execution with time divisor
    ]

    try:
        exit_code = subprocess.call(script_command)

        metadata and print_footer(metadata)
        return exit_code
    except KeyboardInterrupt:
        return 2


def parse_metadata(path: str) -> Optional[dict]:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        cprint(f"[scl] Metadata file does not exist: '{path}'", "red", attrs=["bold"])
    except Exception as e:
        cprint(f"[scl] Internal error while parsing the metadata in '{path}'", "red", attrs=["bold"])
        traceback.print_exc()
    return None


def print_header(metadata: dict) -> None:
    command = shlex.join(metadata["command"])
    user = metadata["user"]
    hostname = metadata["hostname"]
    start_time = metadata["start_time"]

    cprint(f"[scl] Command executed by {user}@{hostname} at {start_time}", "blue", attrs=["bold"])
    cprint(f"[scl] Command: {command}", "blue", attrs=["bold"])


def print_footer(metadata: dict) -> None:
    end_time = metadata["end_time"]
    status_code = metadata["status_code"]
    error_message = metadata["error_message"]

    if status_code == -1:
        cprint(f"[scl] Exited at {end_time} because of internal error", "red", attrs=["bold"])
        cprint(f"[scl] Error message: {error_message}", "red", attrs=["bold"])
    else:
        color = "green" if status_code == 0 else "red"
        cprint(f"[scl] Exited at {end_time} with code {status_code}", color, attrs=["bold"])


def remove_extension(path: str) -> str:
    for extension in EXTENSIONS:
        if path.endswith(extension):
            return path[:-len(extension)]
    return path


def main_replay(arguments: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="the output file containing the command output")
    ap.add_argument("-v", "--version", action="version", version=get_version_string())
    args = ap.parse_args(arguments)


    # Allow specifying the basename (like ~/.shell-command-logs/echo/2022w11g_133650_63ff),
    # or either file (the *.log or the *.time). If a file with the extention is given, the extension is removed
    path = remove_extension(args.path)

    exit_code = replay_command(path)
    return exit_code


if __name__ == "__main__":
    arguments = sys.argv[1:]
    exit_code = main_replay(arguments)
    sys.exit(exit_code)
