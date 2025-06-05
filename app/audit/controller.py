# app/audit/controller.py

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
import json
from loguru import logger

from app.audit.service import AuditService
from app.model import BaseResponseModel

router = APIRouter()

@router.get("", response_model=BaseResponseModel, tags=["Audit"])
async def health_check():
    return BaseResponseModel(message="Audit service is up")

@router.post("/manual", response_model=BaseResponseModel, tags=["Audit"])
async def manual_audit_trigger(data: dict, audit_svc: AuditService = Depends()):
    endpoint = data.get("endpoint")
    if not endpoint:
        raise HTTPException(status_code=400, detail="Missing endpoint for manual audit")
    req_b = data.get("request_body", {})
    res_b = data.get("response_body", {})
    created_by = data.get("created_by", None)

    class DummyReq:
        def __init__(self, path, body):
            self.url = type("U", (), {"path": path})
            self.method = "POST"
            self._body = json.dumps(body).encode("utf-8")
            self.query_params = {}
            self.state = type("S", (), {"user": None})

        async def json(self):
            return req_b

        async def body(self):
            return self._body

    class DummyRes:
        def __init__(self, body, status_code):
            self.body = json.dumps(body).encode("utf-8")
            self.status_code = status_code

    dummy_req = DummyReq(endpoint, req_b)
    dummy_res = DummyRes(res_b, 200)
    await audit_svc.audit(dummy_req, dummy_res)
    return BaseResponseModel(message="Manual audit triggered")
