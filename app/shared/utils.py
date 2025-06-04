import json
from typing import Any, Dict
from fastapi import Request, UploadFile
from .exceptions import BadRequestException


def load_json_body(request: Request) -> Dict[str, Any]:
    try:
        return request.json()
    except Exception:
        raise BadRequestException("Invalid JSON payload.")


def read_upload_file(file: UploadFile) -> bytes:
    content = file.file.read()
    if not content:
        raise BadRequestException(f"Uploaded file {file.filename} is empty.")
    return content
