"""Wasabi S3 upload module."""
from pathlib import Path
from typing import Dict, Union
import boto3
from botocore.exceptions import ClientError

from config import (
    WASABI_ACCESS_KEY_ID,
    WASABI_SECRET_ACCESS_KEY,
    WASABI_REGION,
    WASABI_ENDPOINT,
    WASABI_BUCKET_NAME,
)

class Wasabi:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=WASABI_REGION,
            endpoint_url=WASABI_ENDPOINT,
            aws_access_key_id=WASABI_ACCESS_KEY_ID,
            aws_secret_access_key=WASABI_SECRET_ACCESS_KEY,
        )
        self.bucket_name = WASABI_BUCKET_NAME

    def upload_file(self, file_path, key):
        try:
            file_path = Path(file_path)
            filename = file_path.name
            local_file_size = file_path.stat().st_size

            try:
                existing_object = self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )

                if existing_object["ContentLength"] == local_file_size:
                    return {
                        "ok": False,
                        "msg": f"File {key} already exists and is complete, skipping upload"
                    }
                print(f"File {key} exists but size differs, re-uploading")

            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    print(f"Uploading {filename} to Wasabi...")
                else:
                    return {"ok": False, "msg": "Something went wrong checking file existence"}

            self.client.upload_file(
                str(file_path),
                self.bucket_name,
                key
            )
            print(f"File uploaded to wasabi: {key}")
            return {"ok": True, "msg": f"File {key} uploaded"}

        except Exception as e:
            return {"ok": False, "msg": str(e)}

wasabi = Wasabi() 