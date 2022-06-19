import base64
import json
import os
import time
import secrets

from shell_command_logger.logger.base_class import RecordingOptions
# local
from .config import SclConfig
from shell_command_logger.backports import List


# This also works when the file is a symlink (gets the original dir)
REAL_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


# @LINK: Opposite of pretty_exec.py:decode_command()
def encode_command(command_and_arguments: List[str]) -> str:
    command_json = json.dumps(command_and_arguments)
    command_json_bytes = command_json.encode("utf-8")
    encoded_command = base64.b64encode(command_json_bytes)
    return encoded_command.decode("utf-8")


# TODO: properly parse the options
def record_command(scl_config: SclConfig, command_and_arguments: List[str], output_file: str, options: RecordingOptions = RecordingOptions()) -> int:
    pretty_exec = os.path.join(REAL_SCRIPT_DIR, "pretty_exec.py")
    encoded_command = encode_command(command_and_arguments)
    inner_command = ["python3", pretty_exec, encoded_command, f"{output_file}.json"]

    try:
        return scl_config.backend.log_command(inner_command, output_file, options)
    except KeyboardInterrupt:
        return 2


def get_timestamp_filename(scl_config: SclConfig) -> str:
    now = time.gmtime()
    date = time.strftime("%Gw%V")
    day = "abcdefg"[now.tm_wday] # Monday -> a, ..., Sunday -> g
    time_str = time.strftime("%H%M%S")
    random = secrets.token_hex(scl_config.file_name_random_bytes) # a random value to (with a high likelyhood) prevent mutiple logs started in the same second from overwriting each other.
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
        if not path:
            raise Exception("The PATH variable is not set. You are running this on Linux, right?")
        for p in path.split(os.path.pathsep):
            p = os.path.join(p, command_name)
            if os.path.exists(p) and os.access(p,os.X_OK):
                if not os.path.samefile(p, calling_scripts__file__value):
                    return p
        # Maybe it is a shell builtin? Just return the original value
        return command_name
        # raise Exception(f"No binary found for '{command_name}', that is not a link to this script")

