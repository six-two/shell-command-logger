import shlex
import sys
# Tested on Arch Linux, but should work on pretty much any Linux distro
from ..backports import List
# from ..config import SclConfig
from .base_class import LoggerBackend, LoggerException, ReplayOptions, RecordingOptions

class LoggerScriptLinux(LoggerBackend):
    """
    A logger based on the Linux tools "script" and "scriptreplay", that are almost always automatically installed
    """
    name = "script_linux"

    def __init__(self) -> None:
        super().__init__()
        if sys.platform.startswith("darwin"):
            raise LoggerException(f"This module does not work on macOS, since the script binary has different options")

    
    def _build_log_command(self, command: List[str], base_file_name: str, options: RecordingOptions) -> List[str]:
        script_command = [
            "script",
            "--log-out", f"{base_file_name}.log", # stores the output
            "--log-timing", f"{base_file_name}.time", # also stores the timing, so that the output can be played back to watch when what happened
            "--command", shlex.join(command), # runs our command, which displays the command, timestamp, exit code, etc
            "--return", # return exit code of the child process
            "--output-limit", str(options.output_limit), # If the output is larger than this, something probably went wrong.
            # This prevents your harddrive from overflowing.
            "--quiet", # Hide the "Script started/stopped" messages
        ]

        return script_command


    def _build_replay_command(self, base_file_name: str, options: ReplayOptions) -> List[str]:
        speed = "1000000" if options.replay_speed == 0 else str(options.replay_speed)

        script_command = [
            "scriptreplay",
            "--log-out", f"{base_file_name}.log", # read the output file
            "--log-timing", f"{base_file_name}.time", # also read the timing file
            "--divisor", speed, # The replay speed
        ]

        return script_command
