#!/usr/bin/env python3
import argparse
import subprocess
import sys


def replay_command(output_file: str) -> int:
    script_command = [
        "scriptreplay",
        "--log-out", f"{output_file}.log", # read the output file
        "--log-timing", f"{output_file}.time", # also read the timing file
        # @TODO: --divisor <num>     speed up or slow down execution with time divisor
    ]

    try:
        exit_code = subprocess.call(script_command)
        return exit_code
    except KeyboardInterrupt:
        return 2


def main_replay(arguments: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="the output file containing the command output")
    args = ap.parse_args(arguments)

    # Allow specifying the basename (like ~/.shell-command-logs/echo/2022w11g_133650_63ff),
    # or either file (the *.log or the *.time). If a file with the extention is given, the extension is removed
    path = str(args.path)
    if path.endswith(".log"):
        path = path[:-4]
    elif path.endswith(".time"):
        path = path[:-5]

    exit_code = replay_command(path)
    return exit_code


if __name__ == "__main__":
    arguments = sys.argv[1:]
    exit_code = main_replay(arguments)
    sys.exit(exit_code)
