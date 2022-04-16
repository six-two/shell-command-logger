import configparser
import io
import os
import traceback
from typing import NamedTuple
# pip dependencies
from config_path import ConfigPath
from termcolor import cprint

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
        pass
        # TODO: write config file

    return config._replace(output_dir=output_dir)


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
