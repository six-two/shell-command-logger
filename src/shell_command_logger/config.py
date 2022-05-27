from configparser import ConfigParser
import io
import os
import traceback
from typing import NamedTuple
# local
from . import get_name_and_version, print_error, DoNotPrintMeException, cprint

class SclConfig(NamedTuple):
    # output section
    output_dir: str
    add_readme: bool
    # replay section
    command_format: str
    replay_speed: float

CONFIG_FILE = os.path.expanduser("~/.config/shell-command-logger/config")


DEFAULT_CONFIG = SclConfig(
    output_dir="~/.shell-command-logs/",
    add_readme=True,
    command_format="[ {start_time} | {success} ] {command}",
    replay_speed=1.0,
)


def sanitize_config(config: SclConfig) -> SclConfig:
    output_dir = os.path.expanduser(config.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    if config.add_readme:
        create_template_file(output_dir)

    return config._replace(output_dir=output_dir)


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
            
            cprint("[INFO] Created README file in output directory", "blue")
        except Exception:
            print_error("[ERROR] Failed to create the template file", print_stacktrace=True)


def load_config() -> SclConfig:
    try:
        if os.path.isfile(CONFIG_FILE):
            # path exists and config can be read
            return parse_config_file(CONFIG_FILE)
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
        section_output = config["Output"]
        output_dir = section_output.get("DataDirectory", DEFAULT_CONFIG.output_dir)
        add_readme = section_output.getboolean("AddReadmeFile", fallback=DEFAULT_CONFIG.add_readme)

        section_replay = config["Replay"]
        command_format = section_replay.get("CommandFormat", DEFAULT_CONFIG.command_format)
        replay_speed = section_replay.getfloat("ReplaySpeed", DEFAULT_CONFIG.replay_speed)
    except KeyError as e:
        print_error(f"Configuration file is missing section {e}. You can create a valid config file with `scl-config --defaults`")
        raise DoNotPrintMeException()

    return SclConfig(
        output_dir=output_dir,
        add_readme=add_readme,
        command_format=command_format,
        replay_speed=replay_speed,
    )


def config_to_parser(scl_config: SclConfig) -> ConfigParser:
    parser = ConfigParser()
    parser["Output"] = {
        "DataDirectory": scl_config.output_dir,
        "AddReadmeFile": scl_config.add_readme,
    }
    parser["Replay"] = {
        "CommandFormat": scl_config.command_format,
        "ReplaySpeed": scl_config.replay_speed,
    }
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

