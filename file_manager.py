"""File management module."""
from pathlib import Path
from typing import List
import os

def get_all_files(dir_path: Path) -> List[Path]:
    files = []
    try:
        for root, _, filenames in os.walk(str(dir_path)):
            for filename in filenames:
                files.append(Path(os.path.join(root, filename)))
        return files
    except Exception as e:
        print(f"Error reading directory {dir_path}: {e}")
        return []

def delete_file(file_path: Path) -> None:
    try:
        file_path.unlink()
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
