from functools import wraps
import logging
from typing import Callable

_DEBUG_FUNCTIONS = False

def init_debugging(enabled: bool, debug_functions: bool = True) -> None:
    """
    Initialize the debugging functionality.
    Enabled is the master switch, which turns all functions on/off.
    If you only want to use specefic debugging functionality, use 'enabled=True' and disable all unwanted flags
    """
    global _DEBUG_FUNCTIONS
    _DEBUG_FUNCTIONS = enabled and debug_functions

    if enabled:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")
        logging.info("Enabled debugging mode")

def debug_function(function: Callable) -> Callable:
    @wraps(function)
    def wrapped(*args, **kwargs):
        if _DEBUG_FUNCTIONS:
            argument_string = f"args={list(args)}, kwargs={kwargs}" if kwargs else list(args)
            logging.debug(f"[Function {function.__name__}] Called with arguments: {argument_string}")
        return_value = function(*args, **kwargs)
        if _DEBUG_FUNCTIONS:
            logging.debug(f"[Function {function.__name__}] Returned value: {repr(return_value)}")
        return return_value

    return wrapped

