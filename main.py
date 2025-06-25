import re
import requests
from pathlib import Path
from filelock import FileLock
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import MEDIA_FOLDER_PATH, LOCK_FILE_PATH
from wasabi import wasabi
from hydrax import hydrax
from file_manager import get_all_files, delete_file
from failed import failed_service

def process_file(file_path):
    filename = file_path.name

    if not filename_regex.match(filename):
        failed_service.add(
            file=str(file_path),
            stage="start",
            message="Invalid filename"
        )
        print(f"Invalid filename: {filename}")
        return

    relative_path = Path(str(file_path).split("TV Shows", 1)[-1]).as_posix().lstrip("/")
    key = f"media/{relative_path}"

    wasabi_res = wasabi.upload_file(file_path, key)
    if not wasabi_res["ok"]:
        failed_service.add(
            file=str(file_path),
            stage="wasabi",
            message=wasabi_res["message"]
        )
        print(wasabi_res["message"])
        return

    hydrax_res = hydrax.upload_file(file_path)
    if not hydrax_res["ok"]:
        failed_service.add(
            file=str(file_path),
            stage="hydrax",
            message=hydrax_res["message"]
        )
        print(hydrax_res["message"])
        return

    try:
        requests.get(f"https://catoonhub.com/api/hydrax/{hydrax_res['res']}?filename={filename}")
    except Exception as e:
        print(f"Error notifying completion: {e}")

    if hydrax_res["ok"] and wasabi_res["ok"]:
        delete_file(file_path)

def main():
    media_folder = Path(MEDIA_FOLDER_PATH)
    
    if not media_folder.exists():
        print(f"Media folder {media_folder} does not exist")
        return

    filename_regex = re.compile(
        r"^.+-(TV|MOVIE)-\d+-S\d{2}-E\d{2}(?:-(\[[A-Z]{2,3}(?:\+[A-Z]{2,3})*\]|[A-Z]{2,3}))?(\.[^.]+)?$",
        re.IGNORECASE
    )

    lock = FileLock(LOCK_FILE_PATH)
    
    try:
        with lock:
            files = get_all_files(media_folder)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_file, file_path) for file_path in files]
            for _ in as_completed(futures):
                pass
        
        failed_service.save()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 