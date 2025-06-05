# app/model.py

from datetime import datetime
from pydantic import BaseModel
from starlette import status

class BaseResponseModel(BaseModel):
    status_code: int = status.HTTP_200_OK
    message: str
    timestamp: str = datetime.utcnow().isoformat()

class CustomException(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code

    def __str__(self) -> str:
        return self.detail
