# app/audit/service.py

import json
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response

from app.shared.audit_dto import audit_dto
from app.config import settings

class AuditService:
    async def audit(self, request: Request, response: Response):
        try:
            endpoint = request.url.path

            # Extract request payload
            if request.method in ("GET", "DELETE"):
                request_payload = dict(request.query_params)
            else:
                try:
                    request_payload = await request.json()
                except Exception:
                    raw = await request.body()
                    request_payload = {"raw_body": raw.decode("utf-8", errors="ignore")}

            # Extract response payload
            try:
                raw_resp = response.body.decode("utf-8", errors="ignore")
                if raw_resp:
                    resp_payload = json.loads(raw_resp)
                else:
                    resp_payload = {"status_code": response.status_code}
            except Exception:
                resp_payload = {"status_code": response.status_code}

            created_by = None
            if hasattr(request.state, "user") and request.state.user:
                created_by = getattr(request.state.user, "display_name", None) \
                             or getattr(request.state.user, "preferred_username", None)

            await audit_dto.insert_event(
                endpoint=endpoint,
                request_payload=request_payload,
                response_payload=resp_payload,
                created_by=created_by
            )
        except Exception as e:
            logger.error(f"[AuditService] Failed auditing: {e}")
