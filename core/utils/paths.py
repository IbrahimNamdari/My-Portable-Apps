import os
import sys
from typing import Union


def resource_path(relative_path: str) -> Union[str, os.PathLike]:
    """
    Get the absolute path to a resource file, which is compatible with
    both a standard Python environment and a PyInstaller-bundled executable.

    PyInstaller packages all resources into a temporary directory at runtime.
    This function detects that temporary path and constructs the correct
    file path. In a normal development environment, it uses the current
    working directory as the base path.

    Args:
        relative_path: The path to the resource relative to the project root.

    Returns:
        The absolute path to the specified resource.
    """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS.
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running in a PyInstaller bundle, use the current directory.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)