import logging
import os

from pathlib import Path

logging.basicConfig(level=logging.INFO)


# Resolve a file path by checking multiple possible locations
def resolve_file_path(file_path: str) -> Path:
    # if file_path is a file that exists, return it
    pathlib_file_path = Path(file_path)

    if pathlib_file_path.is_file():
        logging.debug(f"File already found at given path: {file_path}")
        return file_path

    # this file is at src/utils/file_utils.py, so go up three levels to the project root
    project_root = Path(__file__).resolve().parent.parent.parent
    logging.debug(f"Resolving project root: {project_root}")

    # try to resolve relative to project root
    file_path_relative_to_project_root = project_root / file_path
    if file_path_relative_to_project_root.is_file():
        logging.debug(
            f"File found at given path relative to root: {file_path_relative_to_project_root}"
        )
        return file_path_relative_to_project_root

    # try to resolve relative to current working directory
    file_path_relative_to_cwd = Path(os.getcwd()) / file_path
    if file_path_relative_to_cwd.is_file():
        logging.debug(
            f"File found at given path relative to cwd: {file_path_relative_to_cwd}"
        )
        return file_path_relative_to_cwd

    # try to resolve relative to asset directory
    asset_directory = Path(__file__).resolve().parent / "assets"
    file_path_relative_to_asset = asset_directory / file_path
    if file_path_relative_to_asset.is_file():
        logging.debug(
            f"File found at given path (relative to asset): {file_path_relative_to_asset}"
        )
        return file_path_relative_to_asset

    raise FileNotFoundError(f"File not found: {file_path}")
