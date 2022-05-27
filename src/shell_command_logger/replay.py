#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import subprocess
import sys
import traceback
from typing import Optional
# local
from . import get_version_string, print_error, backports, cprint
from .config import load_config, sanitize_config, SclConfig

EXTENSIONS = [".json", ".log", ".time"]
# @TODO: read from config
FZF_PATH = "fzf"


def replay_command(output_file: str, scl_config: SclConfig) -> int:
    metadata = parse_metadata(f"{output_file}.json")
    
    if metadata:
        print_header(metadata)

    script_command = [
        "scriptreplay",
        "--log-out", f"{output_file}.log", # read the output file
        "--log-timing", f"{output_file}.time", # also read the timing file
        "--divisor", str(scl_config.replay_speed),# @TODO why does this finish immediately with values > 1?
    ]

    try:
        exit_code = subprocess.call(script_command)

        if metadata:
            print_footer(metadata)
        return exit_code
    except KeyboardInterrupt:
        return 2


def parse_metadata(path: str) -> Optional[dict]:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"Metadata file does not exist: '{path}'")
    except Exception as e:
        print_error(f"Internal error while parsing the metadata in '{path}'", print_stacktrace=True)
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


def select_file(scl_config: SclConfig) -> Optional[str]:
    log_files = backports.root_dir_glob("**/*.log", root_dir=scl_config.output_dir, recursive=True)
    if not log_files:
        cprint("No command log files found!", "red")
        return None
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
            return None
        
        if process_result.returncode == 0:
            fzf_choice = process_result.stdout.decode().strip()
            return os.path.join(scl_config.output_dir, fzf_choice)
        else:
            cprint(f"fzf failed with code {process_result.returncode}")
            return None


def select_command(scl_config: SclConfig) -> Optional[str]:
    log_files = backports.root_dir_glob("**/*.json", root_dir=scl_config.output_dir, recursive=True)
    if not log_files:
        cprint("No command log files found!", "red")
        return None
    elif len(log_files) == 1:
        # automatically return the only match
        only_choice = log_files[0]
        return os.path.join(scl_config.output_dir, only_choice)
    else:
        log_files = [os.path.join(scl_config.output_dir, x) for x in sorted(log_files)]
        log_file_labels = [CommandFormater(x).format_command(scl_config.command_format).strip()
                            for x in log_files]
        # use fzf to let the user select the file
        log_files_text = "\n".join(sorted(log_file_labels))
        # Pass choices via stdin, read result from stdout, pass through stderr to show the menu
        try:
            process_result = subprocess.run([FZF_PATH], input=log_files_text.encode(), stdout=subprocess.PIPE)
        except FileNotFoundError:
            cprint(f"[ERROR] Program '{FZF_PATH}' not found. Please install it (and add it to your $PATH)", "red", attrs=["bold"])
            return None
        
        if process_result.returncode == 0:
            fzf_choice = process_result.stdout.decode().strip()
            fzf_index = log_file_labels.index(fzf_choice)
            return log_files[fzf_index]
        else:
            cprint(f"[ERROR] fzf failed with code {process_result.returncode}", "red")
            return None

class CommandFormater:
    def __init__(self, metadata_file: str) -> None:
        with open(metadata_file, "r") as f:
            self.metadata = json.load(f)

    def get_time(self, name: str) -> str:
        time = self.metadata.get(name, "<unknown time>")
        # Remove time zone
        time = time.split("+")[0]
        # convert Z to space to visually separate the date from the time
        time = time.replace("Z", " ")
        return time

    def get_statuscode_and_success(self) -> tuple[str, str]:
        status_code = self.metadata.get("status_code")
        status_code = "N/A" if status_code == -1 else str(status_code)
        # checkmark if success else cross
        success = "✔" if status_code == "0" else "✖"
        return (status_code, success)

    def get_command(self) -> str:
        command = self.metadata.get("command")
        return shlex.join(command) if command is not None else "<unknown command>"

    def format_command(self, command_format: str) -> str:
        command = self.get_command()
        end_time = self.get_time("end_time")
        hostname = self.metadata.get("hostname", "<unknown hostname>")
        start_time = self.get_time("start_time")
        status_code, success = self.get_statuscode_and_success()
        username = self.metadata.get("user", "<unknown user>")
        try:
            return command_format.format(
                command=command,
                end_time=end_time,
                hostname=hostname,
                start_time=start_time,
                status_code=status_code,
                success=success,
                username=username,
            )
        except KeyError as e:
            print_error(f"The variable {e} is not a valid placeholder for the command format", raise_error=True)
            raise Exception("BUG: This code should not be reachable")
