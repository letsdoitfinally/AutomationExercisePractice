import uuid
import json
from pathlib import Path
from typing import Union



def generate_unique_id() -> str:
    """Generate a unique email address for test execution.

    Returns:
        A unique email address that can be used for signup testing.
    """
    unique_id = uuid.uuid4().hex[:8]
    return unique_id


def load_json_data(file_path: Union[str, Path]) -> dict:
    """This method will load the json data in dictionary format.

    Args:
        file_path: json data file path as a string or Path object

    Returns:
        data in dictionary format
    """
    # Check if the input is a Path object, if so, convert or handle it
    if isinstance(file_path, Path):
        # You can use target_path.open() style directly here
        with file_path.open(mode='r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Fallback to standard open() if it is a string path
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)

    return data

