import logging
import nbformat
from nbconvert import PythonExporter
from utils.file import write_file


async def convert_notebook_to_script(notebook_path, script_path):
    """
    Convert a Jupyter Notebook to a Python script.

    Parameters:
    - notebook_path (str): The path to the Jupyter Notebook file.
    - script_path (str): The path to save the converted Python script.
    """
    # Load the Jupyter notebook
    with open(notebook_path, "r") as notebook_file:
        notebook_content = nbformat.read(notebook_file, as_version=4)

    # Convert the notebook to a Python script
    python_exporter = PythonExporter()
    python_script, _ = python_exporter.from_notebook_node(notebook_content)

    # Write the Python script to a file
    await write_file(python_script, script_path, "w")

    logging.info(f"Notebook '{notebook_path}' has been converted to '{script_path}'.")
