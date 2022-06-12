import shutil
import subprocess
# local files
from shell_command_logger import print_color
from shell_command_logger.config import load_config, sanitize_config

SUBCOMMAND_NAMES = ["check"]
ARG_PARSER_OPTIONS = {
    "description": "This command checks if the program is properly installed and if all dependencies are installed. If any required dependencies are not met, the programm will fail with error code 1. If only optional dependencies are missing, the program will finish successful.",
    "help": "check if dependencies are satisfied",
}

def populate_agrument_parser(ap) -> None:
    """
    Populates an argparse.ArgumentParser or an subcommand argument parser
    """
    pass


def subcommand_main(args) -> int:
    """
    This method expects the parsed arguments from an argument parser that was set up with `populate_agrument_parser()`.
    It returns an unix-like status code (0 -> success, everything else -> error).
    """
    checker = DependencyChecker()
    checker.check_binary("script", True, "logging command output")
    checker.check_binary("scriptreplay", True, "replaying logged commands") # TODO: make this optional?
    checker.check_binary("grep", False, "searching command output")
    checker.check_python_package("termcolor", "termcolor", False, "colored output")
    checker.check_python_package("python-dateutil", "dateutil", False, "better date parsing")

    # Load the config as late as possible, since it may cause an exception
    scl_config = sanitize_config(load_config())
    checker.check_interactive_selection(scl_config.fzf_executable, False, "selecting which command to replay")

    # Return 0 if all required dependencies are satisfied
    return 1 if checker.required_missing else 0


class DependencyChecker:
    def __init__(self) -> None:
        self.required_missing = False

    def check_binary(self, name: str, required: bool, reason: str) -> None:
        print(f"Binary '{name}' is ", end="")
        if shutil.which(name):
            print_color("installed", "green", bold=required)
        else:
            self._handle_missing(required, reason)

    def check_python_package(self, pip_package_name: str, package_to_import: str, required: bool, reason: str) -> None:
        """
        Two names are required, since some packages have different names (for example PyYAML, which is imported as 'yaml')
        """
        print(f"Python package '{pip_package_name}' is ", end="")
        try:
            __import__(package_to_import)
            print_color("installed", "green", bold=required)
        except ImportError:
            self._handle_missing(required, reason)
            print_color(f" -> Can be installed with: python3 -m pip install {pip_package_name}", "yellow")

    def _handle_missing(self, required: bool, reason: str, status="missing") -> None:
        if required:
            # Store that a required dependency is missing
            self.required_missing = True
        print_color(status, "red", bold=required)
        dependency_type = "Required" if required else "Optional"
        print_color(f" -> {dependency_type} dependency: Used for {reason}", "yellow", bold=required)

    def check_interactive_selection(self, command: str, required: bool, reason: str) -> None:
        print(f"Command for interactive selection ({command}) ", end="")
        try:
            correct_choice = b"correct choice"
            input_bytes = b"Please select '" + correct_choice + b"' from the choices offered:\nDo not select me\n" + correct_choice + b"\nAnother bad choice"
            result = subprocess.run(command, shell=True, input=input_bytes, stdout=subprocess.PIPE)
            if result.returncode == 0:
                output = result.stdout.decode().strip()
                if output == correct_choice.decode():
                    print_color("returned expected result", "green", bold=required)
                    return
                else:
                    self._handle_missing(required, reason, "returned unexpected value")
            else:
                self._handle_missing(required, reason, f"exited with error (code {result.returncode})")
        except Exception as ex:
            self._handle_missing(required, reason, f"caused an error: {ex}")
        print_color(f" -> You set a custom command with: scl config --set fzf-command 'put your command here'", "yellow")

