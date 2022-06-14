import os
from typing import Optional

_PYTHON_MAIN_FILE: Optional[str] = None


def get_python_main_file() -> str:
    if _PYTHON_MAIN_FILE:
        return _PYTHON_MAIN_FILE
    else:
        raise Exception("_PYTHON_MAIN_FILE is not set")


def set_python_main_file(new_value: str, allow_overwrite: bool = False) -> None:
    global _PYTHON_MAIN_FILE
    if new_value:
        if _PYTHON_MAIN_FILE:
            if allow_overwrite:
                # Overwrite the old value
                _PYTHON_MAIN_FILE = new_value
            else:
                # Overwrite, but 'allow_overwrite' flag is not passed
                raise Exception("_PYTHON_MAIN_FILE is already set, but the 'allow_overwrite' flag is not set")
        else:
            # Set initial value
            _PYTHON_MAIN_FILE = new_value
    else:
        raise Exception("'new_value' is empty")


def is_same_as_main_file(other_file: str) -> bool:
    main_file = get_python_main_file()
    return os.path.samefile(main_file, other_file)
