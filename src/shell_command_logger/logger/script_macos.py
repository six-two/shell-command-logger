import sys
# Tested on macOS Monterey (Version 12.4), may not work on older versions
from .. import print_color
from ..backports import List
from .base_class import LoggerBackend, LoggerException, ReplayOptions, RecordingOptions

class LoggerScriptMacOs(LoggerBackend):
    """
    A logger based on the macOS tool "script", that is automatically installed (I think, may also be part of Xcode or something like that) 
    """
    name = "script_macos"

    def __init__(self) -> None:
        super().__init__()
        # This tool is only available on macOS, but a tool with the same name exists on linux. To prevent confusion, we check it 
        if sys.platform != "darwin":
            raise LoggerException(f"This tool is only available on macOS. Found different operating system: {sys.platform}")

    
    def _build_log_command(self, command: List[str], base_file_name: str, options: RecordingOptions) -> List[str]:
        script_command = [
            "script", # The tool used to record the output
            "-q", # Quiet mode: do not show the "Script started..." and "Script done..." lines
        ]
        if options.allow_recording_of_stdin:
            # Record a session with input, output, and timestamping.
            # Without this flag, only the output of the command is recorded
            script_command.append("-r")

        # The file to store the results in
        log_file = self.get_output_file_name(base_file_name)
        script_command.append(log_file)

        # The command to execute by script
        script_command += command

        return script_command


    def _build_replay_command(self, base_file_name: str, options: ReplayOptions) -> List[str]:
        log_file = self.get_output_file_name(base_file_name)

        script_command = [
            "script", # The tool used to replaying the output
            "-q", # Quiet mode: do not show the "Script started..." and "Script done..." lines
            "-p", # Replay the output
        ]

        # Handle the replay speed
        if options.replay_speed == 0:
            #      -d      When playing back a session with the -p flag, do not sleep between records when playing back a
            #              timestamped session.
            script_command.append("-d")
        else:
            # I have not seen an option for the replay speed, so we will just print a warning if there is a missmatch
            if options.replay_speed != 1:
                print_color("[Module script_macos] Replay speed is not supported, replaying at original speed", "yellow")

        # The file to replay
        log_file = self.get_output_file_name(base_file_name)
        script_command.append(log_file)

        return script_command


    def get_output_file_name(self, base_file_name: str) -> str:
        return base_file_name + ".script_macos"
