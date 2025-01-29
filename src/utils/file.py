import logging
import os
import glob
import shutil
from fastapi import UploadFile


def delete_all_files_in_path(path: str) -> None:
    """
    Delete all files in the specified path.

    Parameters:
    - path (str): The path to the folder.
    """
    files = glob.glob(os.path.join(path, "*"))
    for file in files:
        try:
            os.remove(file)
            logging.info(f"Deleted: {file}")
        except Exception as e:
            logging.error(f"Error deleting {file}: {e}")


def copy_file(source_path: str, destination_path: str) -> None:
    """
    Copy a file from the source path to the destination path.

    Parameters:
    - source_path (str): The path to the source file.
    - destination_path (str): The path to the destination directory.
    """
    try:
        shutil.copy(source_path, destination_path)
        logging.info(f"File '{source_path}' has been copied to '{destination_path}'.")
    except Exception as e:
        logging.error(f"Error copying file: {e}")


async def write_file(
    file: UploadFile | str, file_location: str, mode: str = "wb"
) -> None:
    """
    Write the contents of an uploaded file to a specified location.

    Parameters:
    - file (UploadFile): The uploaded file.
    - file_location (str): The location to save the file.
    - mode (str): The file mode (default is 'wb').
    """
    with open(file_location, mode) as f:
        if isinstance(file, str):
            f.write(file)
        else:
            f.write(await file.read())
        logging.info(f"File saved to: {file_location}")
