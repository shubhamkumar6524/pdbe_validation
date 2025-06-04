import json
from typing import List
import boto3
from loguru import logger
from app.config import settings

class AuditDto:

    def __init__(self, client) -> None:
        self.__dynamo_client = client

    def insert_event(self, session_id: str, event: dict) -> bool:
        try:
            if not session_id or len(session_id) == 0 or not event or len(event) == 0:
                raise Exception(f"Audit request missing either valid key or event. session_id: {session_id}, event: {event}")
            logger.info(f"Inserting event into audit table. session_id: {session_id}")
            entry: Audit = self.get_audit(session_id=session_id)
            if not entry:
                entry = Audit(session_id=session_id)
            entry.events.append(Event( ** event))
            result = self.__dynamo_client.put_item(
            Item={
            "id": entry.session_id,
            "audit": entry.to_json(),
            "created_on": event.get("created_on"),
            "created_by": event.get("created_by")
            }
        )
            # logger.info(f"Inserted entry into audit table. result: (result['ResponseMetadata']['HTTPStatusCode']]")
            return result
        except Exception as e:
            raise Exception(f"Error while inserting entry into audit table. Reason: {str(e)}")
        

class Event:
    def __init__(self, path: str, request: str, response: str, created_by: str, created_on: str) -> None:
        self.path = path
        self.request = request
        self.response = response
        self.created_on = created_on
        self.created_by = created_by

    @staticmethod
    def from_json(string: str):
        dict_obj = json.loads(string)
        return Event(
            path=dict_obj.get('path'),
            request=dict_obj.get('request'),
            response=dict_obj.get('response'),
            created_on=dict_obj.get('created_on'),
            created_by=dict_obj.get('created_by'),
        )
        
    @staticmethod
    def from_dict(dict_obj: dict):
        return Event(
        path=dict_obj.get('path'),
        request=dict_obj.get('request'),
        response=dict_obj.get('response'),
        created_on=dict_obj.get('created_on'),
        created_by=dict_obj.get('created_by'),
    )
        

class Audit:
    def _init_(self, session_id: str) -> None:
        if not session_id or len(session_id.strip()) == 0:
            raise Exception(f"Invalid session_id value to create Audit. session_id: (session_id]")
        self.session_id = session_id
        self.events: List[Event] = []

    @staticmethod
    def from_json(string: str):
        dict_obj = json.loads(string)
        audit = Audit(session_id=dict_obj.get('session_id'))
        audit.events = [Event.from_dict(event_str) for event_str in dict_obj.get('events', [])]
        return audit

    @staticmethod
    def from_dict(dict_obj: dict):
        audit = Audit(session_id=dict_obj.get('session_id'))
        audit.events = [Event.from_dict(event_str) for event_str in dict_obj.get('events', [])]
        return audit

    def to_json(self):
        return json.dumps(self, default=vars)

audit_dto = AuditDto(boto3.resource(
'dynamodb',
region_name=settings.get_aws_region()
).Table(settings.get_dynamo_db_table_name_audit()))