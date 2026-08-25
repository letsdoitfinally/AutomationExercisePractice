import uuid
import json


def generate_unique_email() -> str:
    """Generate a unique email address for test execution.

    Returns:
        A unique email address that can be used for signup testing.
    """
    unique_id = uuid.uuid4().hex[:8]
    return f"testuser_{unique_id}@example.com"

def load_json_data(file_path: str) -> dict:
    """
    This method will load the json data in dictionary format
    Args:
        file_path: json data file path

    Returns: data in dictionary format

    """
    with open(file_path,mode='r', encoding='utf-8') as f:
        data = json.load(file_path)
    return data
