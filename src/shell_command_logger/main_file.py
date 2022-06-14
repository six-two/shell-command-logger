import os
import shutil
from typing import Optional
import logging

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


def is_scl_binary_same_as_python_main_file() -> bool:
    """
    Checks it the scl binary is the same file (or a symlink) to the main file
    """
    scl_path = shutil.which("scl")
    if scl_path:
        # Check if the binary is the same file
        return is_same_as_main_file(scl_path)
    else:
        # scl is not in $PATH -> can not be the same
        return False


def get_binary_name_or_path() -> str:
    """
    If the scl binary is in path, return 'scl'. Otherwise return the full path to the main script.
    """
    return "scl" if is_scl_binary_same_as_python_main_file() else get_python_main_file()


def create_symlink_to_main_file(path: str) -> None:
    # Check if the target file already exists
    if os.path.exists(path):
        # Check if it is a symlink to the main file
        if is_same_as_main_file(path):
            # Everything is ok, no need to perform do anything :)
            logging.debug("Symlink %s is already pointing to self", path)
            return
        else:
            # A symlink, but not to this file
            # Delete the old file, then create the symlink later
            os.remove(path)
            logging.debug("Removed incorrect symlink %s", path)

    # At this point the given file should not exist
    # So we can simply create the symlink
    os.symlink(get_python_main_file(), path)
    logging.debug("Created symlink %s", path)

