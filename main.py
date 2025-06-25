import re
import requests
from pathlib import Path
from filelock import FileLock

from config import MEDIA_FOLDER_PATH, LOCK_FILE_PATH
from wasabi import wasabi
from hydrax import hydrax
from file_manager import get_all_files, delete_file
from failed import failed_service

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

            for file_path in files:
                filename = file_path.name

                if not filename_regex.match(filename):
                    print(f"Invalid filename: {filename}")
                    failed_service.add(
                        file=str(file_path),
                        stage="start",
                        message="Invalid filename"
                    )
                    continue

                key = f"media{str(file_path).split('media', 1)[1]}"
                wasabi_res = wasabi.upload_file(file_path, key)

                if not wasabi_res["ok"]:
                    failed_service.add(
                        file=str(file_path),
                        stage="wasabi",
                        message=wasabi_res["message"] 
                    )

                hydrax_res = hydrax.upload_file(file_path)
                if not hydrax_res["ok"]:
                    failed_service.add(
                        file=str(file_path),
                        stage="hydrax",
                        message=hydrax_res["msg"]
                    )

                if hydrax_res["ok"] and wasabi_res["ok"]:
                    delete_file(file_path)

            failed_service.save()

            try:
                requests.get("https://catoonhub.com/api/hydrax")
            except Exception as e:
                print(f"Error notifying completion: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 