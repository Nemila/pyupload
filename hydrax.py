"""Hydrax upload module."""
from pathlib import Path
from typing import Dict, Union, Optional
import mimetypes
import requests

from config import HYDRAX_API_KEY, HYDRAX_BASE_URL

class Hydrax:
    def __init__(self, api_key: str):
        self.base_url = HYDRAX_BASE_URL
        self.api_key = api_key

    @staticmethod
    def _get_content_type(filename: str) -> str:
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            ext = Path(filename).suffix.lower()
            content_types = {
                ".mp4": "video/mp4",
                ".avi": "video/avi",
                ".mkv": "video/x-matroska",
                ".mov": "video/quicktime",
                ".wmv": "video/x-ms-wmv",
                ".flv": "video/x-flv",
                ".webm": "video/webm"
            }
            content_type = content_types.get(ext, "application/octet-stream")
        return content_type

    def upload_file(self, file_path):
        try:
            file_path = Path(file_path)
            filename = file_path.name

            files = {
                "file": (
                    filename,
                    file_path.open("rb"),
                    self._get_content_type(filename)
                )
            }

            print(f"Uploading {filename} to Hydrax...")

            response = requests.post(
                f"{self.base_url}/{self.api_key}",
                files=files,
                stream=True
            )

            data = response.json()

            if not response.ok or not data.get("status"):
                return {"ok": False, "msg": "Failed to upload", "res": None}

            print(f"File uploaded: {data.get('slug')}")

            return {
                "ok": True,
                "msg": "File uploaded",
                "res": data.get("slug")
            }

        except Exception as e:
            return {"ok": False, "msg": str(e), "res": None}

hydrax = Hydrax(HYDRAX_API_KEY) 