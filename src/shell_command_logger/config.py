import configparser
import io
import os
import traceback
from typing import NamedTuple
# pip dependencies
from config_path import ConfigPath
from termcolor import cprint
# local
from . import get_name_and_version

class SclConfig(NamedTuple):
    output_dir: str
    add_readme: bool

CONFIG_PATH = ConfigPath("shell-command-logger", "six-two.dev", ".conf")

DEFAULT_CONFIG = SclConfig(
    output_dir="~/.shell-command-logs/",
    add_readme=True,
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
            cprint("[ERROR] Failed to create the template file", "red")
            traceback.print_exc()


def load_config() -> SclConfig:
    try:
        path = CONFIG_PATH.readFilePath()
        if path:
            # path exists and config can be read
            return parse_config_file(path)
        else:
            # No config file exists
            return DEFAULT_CONFIG
    except Exception:
        cprint("[ERROR] Failed to read config file! Falling back on default configuration", "red", attrs=["bold"])
        traceback.print_exc()
        return DEFAULT_CONFIG


def parse_config_file(path: str) -> SclConfig:
    config = configparser.ConfigParser()
    config.read(path)

    section_output = config["Output"]
    output_dir = section_output.get("DataDirectory", DEFAULT_CONFIG.output_dir)
    add_readme = section_output.getboolean("AddReadmeFile", fallback=DEFAULT_CONFIG.add_readme)

    return SclConfig(
        output_dir=output_dir,
        add_readme=add_readme,
    )
