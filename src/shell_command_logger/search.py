from datetime import datetime
import glob
import json
import os
import sys
from typing import NamedTuple, Optional
# local modules
from shell_command_logger.config import SclConfig


class Metadata(NamedTuple):
    command: list[str]
    user: str
    hostname: str
    start_time_utc: datetime
    end_time_utc: datetime
    error_message: Optional[str]
    status_code: int


def parse_metadata(file_path: str) -> Metadata:
    with open(file_path, "r") as f:
        data = json.load(f)
    
    try:
        command = data["command"]
        if type(command) == list:
            for index, list_item in enumerate(command):
                if type(list_item) != str:
                    raise Exception(f"Entry {index+1} in list field 'command' should be a string, but is '{type(list_item)}'")
        else:
            raise Exception(f"Field 'command' should be a list, but is '{type(command)}'")

        start_time_str = _get_string_field(data, "start_time")
        start_time_utc = datetime.fromisoformat(start_time_str)

        end_time_str = _get_string_field(data, "end_time")
        end_time_utc = datetime.fromisoformat(end_time_str)

        error_message = data.get("error_message")
        if error_message != None and type(error_message) != str:
            raise Exception(f"Field 'error_message' should be None or a string, but is '{type(error_message)}'")

        status_code = data["status_code"]
        if type(status_code) != int:
            raise Exception(f"Field 'status_code' should be an integer, but is '{type(status_code)}'")

        return Metadata(
            command=command,
            user=_get_string_field(data, "user"),
            hostname=_get_string_field(data, "hostname"),
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,#TODO
            error_message=error_message,
            status_code=status_code,
        )
    except KeyError as ex:
        raise Exception(f"Metadata is missing required key: {ex}")


def _get_string_field(data: dict, key: str) -> str:
    field = data[key]
    if type(field) == str:
        return field
    else:
        raise Exception(f"The field '{key}' needs to be a string, but is '{type(field)}'")


class SearchableCommand:
    def __init__(self, metadata_file: str) -> None:
        self.file_path = metadata_file
        self.metadata = parse_metadata(metadata_file)


def get_all_searchable_commands(scl_config: SclConfig) -> list[SearchableCommand]:
    results: list[SearchableCommand] = []
    search_pattern = os.path.join(scl_config.output_dir, "**", "*.json")

    for file_path in glob.glob(search_pattern, recursive=True):
        try:
            r = SearchableCommand(file_path)
            results.append(r)
        except Exception as ex:
            print(f"Error parsing metadata file '{file_path}': ", ex, file=sys.stderr)
    return results
