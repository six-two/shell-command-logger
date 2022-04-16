#!/usr/bin/env python3
import argparse
import glob
import json
import os
import shlex
import subprocess
import sys
import traceback
from typing import Optional
# pip dependency
from termcolor import cprint
# local
from . import get_version_string
from .config import load_config, sanitize_config

EXTENSIONS = [".json", ".log", ".time"]
FZF_PATH = "fzf"


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
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--input", metavar=("path"), help="the input file containing the command output")
    group.add_argument("-f", "--select-file", action="store_true", help="interactively search the file names")
    group.add_argument("-c", "--select-command", action="store_true", help="interactively search the command line arguments")

    ap.add_argument("-v", "--version", action="version", version=get_version_string())
    args = ap.parse_args(arguments)

    if args.input:
        path = args.input
    elif args.select_file:
        path = select_file()
    elif args.select_command:
        path = select_command()
    else:
        raise Exception("Bug: Unreachable code")

    if path:
        # Allow specifying the basename (like ~/.shell-command-logs/echo/2022w11g_133650_63ff),
        # or either file (the *.log or the *.time). If a file with the extention is given, the extension is removed
        path = remove_extension(path)

        # replaay the command
        return replay_command(path)
    else:
        return 1


def select_file() -> Optional[str]:
    scl_config = sanitize_config(load_config())

    log_files = glob.glob("**/*.log", root_dir=scl_config.output_dir, recursive=True)
    if not log_files:
        cprint("No command log files found!", "red")
        return
    elif len(log_files) == 1:
        # automatically return the only match
        only_choice = log_files[0]
        return os.path.join(scl_config.output_dir, only_choice)
    else:
        # use fzf to let the user select the file
        log_files_text = "\n".join(sorted(log_files))
        # Pass choices via stdin, read result from stdout, pass through stderr to show the menu
        try:
            process_result = subprocess.run([FZF_PATH], input=log_files_text.encode(), stdout=subprocess.PIPE)
        except FileNotFoundError:
            cprint(f"[ERROR] Program '{FZF_PATH}' not found. Please install it (and add it to your $PATH)", "red", attrs=["bold"])
            return
        
        if process_result.returncode == 0:
            fzf_choice = process_result.stdout.decode().strip()
            return os.path.join(scl_config.output_dir, fzf_choice)
        else:
            cprint(f"fzf failed with code {process_result.returncode}")
            return


def select_command() -> Optional[str]:
    scl_config = sanitize_config(load_config())

    log_files = glob.glob("**/*.json", root_dir=scl_config.output_dir, recursive=True)
    if not log_files:
        cprint("No command log files found!", "red")
        return
    elif len(log_files) == 1:
        # automatically return the only match
        only_choice = log_files[0]
        return os.path.join(scl_config.output_dir, only_choice)
    else:
        log_files = [os.path.join(scl_config.output_dir, x) for x in sorted(log_files)]
        log_file_labels = [format_command(x).strip() for x in log_files]
        # use fzf to let the user select the file
        log_files_text = "\n".join(sorted(log_file_labels))
        # Pass choices via stdin, read result from stdout, pass through stderr to show the menu
        try:
            process_result = subprocess.run([FZF_PATH], input=log_files_text.encode(), stdout=subprocess.PIPE)
        except FileNotFoundError:
            cprint(f"[ERROR] Program '{FZF_PATH}' not found. Please install it (and add it to your $PATH)", "red", attrs=["bold"])
            return
        
        if process_result.returncode == 0:
            fzf_choice = process_result.stdout.decode().strip()
            fzf_index = log_file_labels.index(fzf_choice)
            return log_files[fzf_index]
        else:
            cprint(f"fzf failed with code {process_result.returncode}")
            return


def format_command(metadata_file: str) -> str:
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    start_time = metadata.get("start_time", "unknown time")
    # Remove time zone
    start_time = start_time.split("+")[0]
    # convert Z to space to visually separate the date from the time
    start_time = start_time.replace("Z", " ")

    command = metadata.get("command", ["unknown command"])
    command = shlex.join(command)

    return f"[{start_time}] {command}"


if __name__ == "__main__":
    arguments = sys.argv[1:]
    exit_code = main_replay(arguments)
    sys.exit(exit_code)
