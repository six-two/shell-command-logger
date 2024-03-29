from configparser import ConfigParser
import io
import os
from typing import NamedTuple

from shell_command_logger.logger import get_best_backend_name, get_logger_backend
# local
from . import get_name_and_version, print_error, DoNotPrintMeException, print_color
from .logger.base_class import LoggerBackend

class InvalidConfigException(Exception):
    pass


class SclConfig(NamedTuple):
    # output settings
    output_dir: str
    add_readme: bool
    script_output_limit: int
    file_name_random_bytes: int
    # replay settings
    command_format: str
    replay_speed: float
    # Run a command to let the user choose a value (for example 'fzf', 'dmenu -l 10', etc). Must read input from stdin and output the selection to stdout
    fzf_executable: str
    # The folder where the symlinks should be stored. Should be part of PATH (first/high priority entry) to function
    symlink_dir: str
    # The backend to use
    backend_name: str
    # This is an instantiated backend, derived from backend_name
    backend: LoggerBackend


CONFIG_FILE = os.path.expanduser("~/.config/shell-command-logger/config")
SYSTEM_CONFIG_FILE = os.path.expanduser("/etc/shell-command-logger/config")
NO_BACKEND_INITIALIZED = LoggerBackend()

_KEY_SECTION = "config"
_KEY_DATA_DIRECTORY = "data-directory"
_KEY_ADD_README_FILE = "create-readme"
_KEY_COMMAND_FORMAT = "command-format"
_KEY_REPLAY_SPEED = "replay-speed"
_KEY_OUTPUT_LIMIT = "script-output-limit"
_KEY_FILE_NAME_RANDOM_BYTES = "file-name-random-bytes"
_KEY_FZF_EXECUTABLE = "fzf-command"
_KEY_SYMLINK_DIR = "symlink-directory"
_KEY_BACKEND = "backend"


DEFAULT_CONFIG = SclConfig(
    output_dir="~/.shell-command-logs/",
    add_readme=True,
    command_format="[ {start_time} | {success} ] {command}",
    replay_speed=1.0,
    script_output_limit=1024*1024*1024, # One gigabyte
    file_name_random_bytes=2,
    fzf_executable="fzf",
    symlink_dir="~/.local/share/shell-command-logger/bin",
    backend_name=get_best_backend_name(),
    backend=NO_BACKEND_INITIALIZED,
)


def sanitize_config(config: SclConfig) -> SclConfig:
    output_dir = os.path.expanduser(config.output_dir)
    symlink_dir = os.path.expanduser(config.symlink_dir)

    ensure_directory_exists(output_dir)
    ensure_directory_exists(symlink_dir)

    if not config.fzf_executable.strip():
        raise InvalidConfigException(f"Setting '{_KEY_FZF_EXECUTABLE}' can not be empty")

    if config.add_readme:
        create_template_file(output_dir)

    if config.replay_speed <= 0:
        raise InvalidConfigException(f"Config setting '{_KEY_REPLAY_SPEED}' needs to be larger than zero")

    if config.file_name_random_bytes < 1 or config.file_name_random_bytes > 100:
        raise InvalidConfigException(f"Config setting '{_KEY_FILE_NAME_RANDOM_BYTES}' needs to be between 1 and 100")

    # Try loading the correct backend module
    try:
        backend = get_logger_backend(config.backend_name)
    except Exception as ex:
        raise InvalidConfigException(f"Failed to load backend '{config.backend_name}': {ex}")

    return config._replace(output_dir=output_dir, symlink_dir=symlink_dir, backend=backend)


def ensure_directory_exists(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        raise InvalidConfigException(f"Could not create directory: '{path}'")

    if not os.access(path, os.R_OK):
        raise InvalidConfigException(f"Missing read permission for directory: '{path}'")

    if not os.access(path, os.W_OK):
        raise InvalidConfigException(f"Missing write permission for directory: '{path}'")


def create_template_file(output_dir: str) -> None:
    output_path = os.path.join(output_dir, "README.md")
    if not os.path.exists(output_path):
        try:
            template_path = os.path.dirname(__file__)
            template_path = os.path.join(template_path, "output_dir_readme_template.md")

            with open(template_path, "r") as f:
                template = f.read()
            
            _, version = get_name_and_version()
            template = template.replace("{{version}}", version)

            with open(output_path, "w") as f:
                f.write(template)
            
            print_color("[INFO] Created README file in output directory", "blue")
        except Exception:
            print_error("[ERROR] Failed to create the template file", print_stacktrace=True)


def load_config() -> SclConfig:
    try:
        if os.path.isfile(CONFIG_FILE):
            # path exists and config can be read
            return parse_config_file(CONFIG_FILE)
        elif os.path.isfile(SYSTEM_CONFIG_FILE):
            # Fall back to system wide configuration
            print_color(f"Loading system wide configuration from {SYSTEM_CONFIG_FILE}", "yellow")
            return parse_config_file(SYSTEM_CONFIG_FILE)
        else:
            # No config file exists
            return DEFAULT_CONFIG
    except DoNotPrintMeException:
        print_error("Failed to read config file! Falling back on default configuration")
        return DEFAULT_CONFIG
    except Exception:
        print_error("Failed to read config file! Falling back on default configuration", print_stacktrace=True)
        return DEFAULT_CONFIG


def parse_config_file(path: str) -> SclConfig:
    config = ConfigParser()
    config.read(path)

    try:
        section_config = config[_KEY_SECTION]
    except KeyError:
        print_error(f"Configuration file is missing section '{_KEY_SECTION}'. You can create a valid config file with `scl config --defaults`")
        raise DoNotPrintMeException()

    # Read values from the config file. If not defined, use the default value
    output_dir = section_config.get(_KEY_DATA_DIRECTORY, DEFAULT_CONFIG.output_dir)
    add_readme = section_config.getboolean(_KEY_ADD_README_FILE, DEFAULT_CONFIG.add_readme)
    command_format = section_config.get(_KEY_COMMAND_FORMAT, DEFAULT_CONFIG.command_format)
    replay_speed = section_config.getfloat(_KEY_REPLAY_SPEED, DEFAULT_CONFIG.replay_speed)
    try:
        script_output_limit = int(section_config.get(_KEY_OUTPUT_LIMIT, str(DEFAULT_CONFIG.script_output_limit)))
    except ValueError: # Handle the case where the input is not a valid number
        script_output_limit = DEFAULT_CONFIG.script_output_limit
    file_name_random_bytes = section_config.getint(_KEY_FILE_NAME_RANDOM_BYTES, DEFAULT_CONFIG.file_name_random_bytes)
    fzf_executable = section_config.get(_KEY_FZF_EXECUTABLE, DEFAULT_CONFIG.fzf_executable)
    symlink_dir = section_config.get(_KEY_SYMLINK_DIR, DEFAULT_CONFIG.symlink_dir)
    backend_name = section_config.get(_KEY_BACKEND, DEFAULT_CONFIG.backend_name)

    return SclConfig(
        output_dir=output_dir,
        add_readme=add_readme,
        command_format=command_format,
        replay_speed=replay_speed,
        script_output_limit=script_output_limit,
        file_name_random_bytes=file_name_random_bytes,
        fzf_executable=fzf_executable,
        symlink_dir=symlink_dir,
        backend_name=backend_name,
        backend=NO_BACKEND_INITIALIZED,
    )


def config_to_parser(scl_config: SclConfig) -> ConfigParser:
    config_as_dict: dict = {
        _KEY_DATA_DIRECTORY: scl_config.output_dir,
        _KEY_ADD_README_FILE: scl_config.add_readme,
        _KEY_COMMAND_FORMAT: scl_config.command_format,
        _KEY_REPLAY_SPEED: scl_config.replay_speed,
        _KEY_OUTPUT_LIMIT: scl_config.script_output_limit,
        _KEY_FILE_NAME_RANDOM_BYTES: scl_config.file_name_random_bytes,
        _KEY_FZF_EXECUTABLE: scl_config.fzf_executable,
        _KEY_SYMLINK_DIR: scl_config.symlink_dir,
        _KEY_BACKEND: scl_config.backend_name,
    }

    parser = ConfigParser()
    parser[_KEY_SECTION] = config_as_dict
    return parser


def parser_to_text(parser: ConfigParser) -> str:
    fake_file = io.StringIO()
    parser.write(fake_file)
    return fake_file.getvalue()


def save_parser_as_config(parser: ConfigParser) -> None:
    # Ensure parent dir exists
    parent_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(parent_dir, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        parser.write(f)
    print(f"Wrote config to '{CONFIG_FILE}':")
    print(parser_to_text(parser).rstrip())

