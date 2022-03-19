#!/usr/bin/env python3
import argparse
import subprocess
import sys


def replay_command(output_file: str) -> int:
    timing_file = f"{output_file}.time"

    script_command = ["scriptreplay",
        "--log-out", output_file, # read the output file
        "--log-timing", timing_file, # also read the timing file
        # @TODO: --divisor <num>     speed up or slow down execution with time divisor
    ]

    try:
        exit_code = subprocess.call(script_command)
        return exit_code
    except KeyboardInterrupt:
        return 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="the output file containing the command output")
    args = ap.parse_args()

    exit_code = replay_command(args.path)
    sys.exit(exit_code)
