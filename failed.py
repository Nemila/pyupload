"""Failed uploads tracking module."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal

from config import FAILED_FILE_PATH

class FailedService:
    def __init__(self):
        self.failed_file = FAILED_FILE_PATH
        self.data: List[Dict] = self._load_data()

    def _load_data(self) -> List[Dict]:
        try:
            if self.failed_file.exists():
                return json.loads(self.failed_file.read_text())
        except Exception as e:
            print(f"Error loading failed data: {e}")
        return []

    def add(
        self,
        file: str,
        stage: Literal["hydrax", "wasabi", "start"],
        message: str
    ) -> None:
        exists = any(
            item["file"] == file
            and item["stage"] == stage
            and item["message"] == message
            for item in self.data
        )
        if exists:
            return

        self.data.append({
            "file": str(file),
            "stage": stage,
            "message": message,
            "date": datetime.now().isoformat()
        })

    def save(self) -> None:
        try:
            self.failed_file.write_text(json.dumps(self.data, indent=2))
            print(f"Recorded {len(self.data)} failures")
        except Exception as e:
            print(f"Error saving failed data: {e}")

failed_service = FailedService() 