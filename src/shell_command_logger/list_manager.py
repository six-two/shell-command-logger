import os
import shutil
from typing import Optional
# local files
from shell_command_logger.backports import List


class ListWrapper:
    """
    This class wrapes a list. It is used, so that you can do stuff like 
    `wrapper.list = [f(x) for x in wrapper.list]`.
    Using a native list would not work, unless the list is modified in-place,
    which makes programming way harder (and more error-prone)
    """
    def __init__(self, initial_list: List[str]) -> None:
        self.list = initial_list


class ListManager:
    """
    This class manages list configuration files (such as aliases).
    It provieds a context manager, that loads the current settings and writes any changes back to the file.
    """
    def __init__(self, state_file: str, default_file: Optional[str]) -> None:
        self.state_file = state_file
        self.default_file = default_file
        # This stores the original list. Only if it is modified, the results will be written back to the file.
        # This assumes, that no one modified the list in the mean time, which is plausible if the object is only used for a short amount of time.
        self.og_list: Optional[List[str]] = None
        # The object returned via __enter__. Will be used by __exit__ to check if the file should be modified
        self.list_wrapper: Optional[ListWrapper] = None


    def get_read_only_list(self) -> List[str]:
        """
        Loads the results from the file. Modifications to the returned list will not be reflected in the file.
        """
        if self.default_file and not os.path.exists(self.state_file):
            # Copy my defaults file over
            parent_dir = os.path.dirname(self.state_file)
            os.makedirs(parent_dir, exist_ok=True)
            shutil.copyfile(self.default_file, self.state_file)

        # Read the lines from the file
        with open(self.state_file, "r") as f:
            lines = f.read().split("\n")

        # Remove leading/trailing whitespace and then empty lines
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if x]
        return lines

    def __enter__(self) -> ListWrapper:
        lines = self.get_read_only_list()

        # Store a copy of the original value
        self.og_list = list(lines)
        self.list_wrapper = ListWrapper(lines)
        return self.list_wrapper

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self.list_wrapper:
            raise Exception("Invalid state, did you call __enter__?")
        values = self.list_wrapper.list
        # remove duplicates and sort the results
        values = sorted(list(set(values)))

        if values != self.og_list:
            # convert list to text
            text = "\n".join(values) + "\n"

            # Write text to file
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w") as f:
                f.write(text)

        # Free up the references        
        self.og_list = None
        self.list_wrapper = None

        # Reraise the exception that ended the `with` block
        return None