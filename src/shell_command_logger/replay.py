import glob
import json
import os
import shlex
import subprocess
import traceback
from typing import Optional, Callable
# local
from . import get_version_string, print_error, backports, print_color
from .config import load_config, sanitize_config, SclConfig, _KEY_FZF_EXECUTABLE

EXTENSIONS = [".json", ".log", ".time"]


def replay_command(output_file: str, scl_config: SclConfig, only_show_original_output: bool = False, skip_replay: bool = False) -> int:
    output_file = remove_extension(output_file)
    metadata = None if only_show_original_output else parse_metadata(f"{output_file}.json")
    
    if metadata:
        print_header(metadata)

    try:
        # Turns out that the .log file has a header (and a footer) and may have a complicated format (see flag "--logging-format" at https://man7.org/linux/man-pages/man1/script.1.html)
        # So instead of reading the file, we use scriptrelay and give it a really big speed up factor.
        speed = "1000000" if skip_replay else str(scl_config.replay_speed)

        # Build the replay command
        script_command = [
            "scriptreplay",
            "--log-out", f"{output_file}.log", # read the output file
            "--log-timing", f"{output_file}.time", # also read the timing file
            "--divisor", speed,
        ]

        # Execute scriptreplay
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

    print_color(f"[scl] Command executed by {user}@{hostname} at {start_time}", "blue", bold=True)
    print_color(f"[scl] Command: {command}", "blue", bold=True)


def print_footer(metadata: dict) -> None:
    end_time = metadata["end_time"]
    status_code = metadata["status_code"]
    error_message = metadata["error_message"]

    if status_code == -1:
        print_color(f"[scl] Exited at {end_time} because of internal error", "red", bold=True)
        print_color(f"[scl] Error message: {error_message}", "red", bold=True)
    else:
        color = "green" if status_code == 0 else "red"
        print_color(f"[scl] Exited at {end_time} with code {status_code}", color, bold=True)


def remove_extension(path: str) -> str:
    for extension in EXTENSIONS:
        if path.endswith(extension):
            return path[:-len(extension)]
    return path


def get_command_file_list(scl_config: SclConfig) -> list[str]:
    pattern = os.path.join(scl_config.output_dir, "**", "*.json")
    return glob.glob(pattern, recursive=True)


def format_filename(metadata_file: str) -> str:
    return metadata_file


def format_command_builder(scl_config: SclConfig) -> Callable:
    def format_function(metadata_file: str) -> str:
        return CommandFormater(metadata_file).format_command(scl_config.command_format)
    return format_function


def select_formatted(scl_config: SclConfig, format_function: Callable[[str], str], log_files: list[str]) -> Optional[str]:
    if not log_files:
        print_color("No command log files found!", "red")
        return None
    elif len(log_files) == 1:
        # automatically return the only match
        only_choice = log_files[0]
        return os.path.join(scl_config.output_dir, only_choice)
    else:
        log_files = [os.path.join(scl_config.output_dir, x) for x in sorted(log_files)]
        log_file_labels = [format_function(x).strip() for x in log_files]
        # use fzf to let the user select the file
        log_files_labels_text = "\n".join(sorted(log_file_labels))
        # Pass choices via stdin, read result from stdout, pass through stderr to show the menu
        try:
            process_result = subprocess.run(scl_config.fzf_executable, shell=True, input=log_files_labels_text.encode(), stdout=subprocess.PIPE)
        except FileNotFoundError as ex:
            print_color(f"[ERROR] Program '{ex}' not found. Please install it and add it to your $PATH (or configure the {_KEY_FZF_EXECUTABLE} setting)", "red", bold=True)
            return None
        
        if process_result.returncode == 0:
            # May contain a trailing newline, so we strip it
            fzf_choice = process_result.stdout.decode().strip()
            fzf_index = log_file_labels.index(fzf_choice)
            return log_files[fzf_index]
        else:
            print_color(f"[ERROR] '{scl_config.fzf_executable}' failed with code {process_result.returncode}", "red", bold=True)
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
