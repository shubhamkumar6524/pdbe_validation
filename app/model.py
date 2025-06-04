from datetime import datetime
from pydantic import BaseModel, Field
from starlette import status


class BaseResponseModel(BaseModel):
    status_code: int = Field(default=status.HTTP_200_OK)
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CustomException(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code

    def __str__(self) -> str:
        return self.detail
