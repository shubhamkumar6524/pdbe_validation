import boto3
from loguru import logger
from app.config import settings
from app. feedback.model import FeedbackRequestModel
from app.app import CustomException
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta

from app.shared.utils import format_datetime_to_iso_format

class ChatHistory:
    def __init__(self, message_id: str, chat_session_id: str, question: str, rephrased_question: str, answer: str, feedback: str, comments: str, created_by: str, created_on: str, question_time: str, answer_time: str) -> None:
        self.message_id = message_id
        self.chat_session_id = chat_session_id
        self.question = question
        self.rephrased_question = rephrased_question
        self.answer = answer
        self.feedback = feedback
        self.comments = comments
        self.created_on = created_on
        self.created_by = created_by
        self.question_time = question_time
        self.answer_time = answer_time
        
    @staticmethod
    def from_dict(dict_obj: dict):
        return ChatHistory(
        message_id=dict_obj.get('id'),
        chat_session_id=dict_obj.get('chat_session_id'),
        question=dict_obj.get('question'),
        rephrased_question=dict_obj.get('rephrased_question'),
        answer=dict_obj.get('answer'),
        feedback=dict_obj.get('feedback'),
        comments=dict_obj.get('comments'),
        created_on=dict_obj.get('created_on'),
        created_by=dict_obj.get('created_by'),
        question_time=dict_obj.get('question_time'),
        answer_time=dict_obj.get('answer_time')
        )
        

class ChatHistoryDto:
    def __init__(self, client) -> None:
        self.__dynamo_client = client

    def add_chat_history(self, chat_history: ChatHistory) -> bool:
        try:
            logger.info(F"Inserting into chat history. chat_session_id: (chat_history.chat_session_id), message_id: (chat_history.message_id]")
            result = self.__dynamo_client.put_item(
                Item={
                "id": chat_history.message_id,
                "created_on": chat_history.created_on,
                "created_by": chat_history.created_by,
                "feedback": chat_history. feedback,
                "chat_session_id": chat_history.chat_session_id,
                "comments": chat_history.comments,
                "question": chat_history.question,
                "rephrased_question":chat_history.rephrased_question,
                "answer": chat_history.answer,
                "answer_time": chat_history.answer_time,
                "question_time": chat_history.question_time
                }
            )
            logger.info(f"Inserted entry into Chat History, result: {result['ResponseMetadata']['HTTPStatusCode']}")
            return result
        except Exception as e:
            raise Exception(f"Error while inserting entry into Chat History Table. Reason: {str(e)}")
        
    def insert_event(self, feedback: FeedbackRequestModel, event: dict) -> bool:
        try:
            if not feedback.chat_session_id or len(feedback.chat_session_id) == 0:
                raise Exception(f"Feedback request missing either valid key or event. chat_session_id: {feedback.chat_session_id}, event: {event}")
            logger.info(F"Fetching chat history. chat_session_id: {feedback.chat_session_id}")
            entry: ChatHistory = self.get_chat_history(feedback.message_id)
            if not entry.feedback:
                entry.feedback = ""
            if not entry.comments:
                entry.comments = ""
            logger.info(f"Feedback update. feedback -> old_value: {entry. feedback}, new_value: {feedback.feedback}, comment -> oldvalue: {entry.comments}, new_value: {feedback.comments}")
            result = self.__dynamo_client.put_item(
                Item={
                    "id": entry.message_id,
                    "created_on": entry.created_on,
                    "created_by": entry.created_by,
                    "feedback": feedback. feedback,
                    "chat_session_id": entry.chat_session_id,
                    "comments": feedback.comments,
                    "question": entry.question,
                    "rephrased_question":entry.rephrased_question,
                    "answer": entry.answer,
                    "answer_time": entry.answer_time,
                    "question_time": entry.question_time
                    }
            )
            logger.info(f"Updated entry into chat History table. result: {result['ResponseMetadata']['HTTPStatusCode']}")
            return result
        except Exception as e:
            raise Exception(f"Error while inserting entry into Chat History Table, Reason: {str(e)}")
        
    def get_chat_history(self, message_id: str) -> ChatHistory:
        try:
            result = self.__dynamo_client.get_item(
                Key={"id": message_id}
            )
            item = result.get('Item', None)
            if not item:
                raise Exception(f"No entry found History Table table. message_id: {message_id}")
            logger.info(f"Fetching for message_id : {message_id} is completed")
            items = ChatHistory.from_dict(item)
            return items
        except Exception as e:
            raise Exception(f"Error fetching entry from chat history table. message_id: {message_id}, Reason: {str(e)}")
        
    def fetch_and_use_rephrased_question_and_answer(self, message_id: str):
        try:
            chat_history = self.get_chat_history(message_id)
            question = chat_history.question
            rephrased_question = chat_history.rephrased_question
            answer = chat_history.answer
            logger.info(f"Rephrased question extracted: {rephrased_question}")
            logger.info(f"Rephrased answer extracted: {answer}")
            return question, rephrased_question, answer
        except Exception as e:
            raise Exception(f"Error fetching or processing the rephrased question and answer. Reason: {str(e)}")
        
    def delete_chat(self, message_id):
        try:
            with self.__dynamo_client.batch_writer() as batch:
                for item in message_id:
                    logger. info(f"Deleted chat from chat history table for message_id: {item}")
                    batch.delete_item(Key={
                        "id": item
                    })
            success_message="Record(s) deleted successfully"
            return success_message
        except Exception as e:
            raise CustomException(f"Error while deleting entry from chat history table. message_ids: {message_id}. Reason: {e .__str__()}")
        
    
    def get_chat_db(self, created_by: str = None, chat_session_id: str = None):
        days_limit = datetime.utcnow() - timedelta(days=settings.get_chat_history_limit_in_days())
        # Convert the date to a string in the same format as stored in DynamoDB
        days_limit_str = format_datetime_to_iso_format(days_limit)
        try:
            if chat_session_id and created_by:
                response = self.__dynamo_client.scan(
                FilterExpression=Attr('created_by').eq(created_by) & Attr('chat_session_id').eq(
                chat_session_id) & Attr('created_on').gte(days_limit_str))
                items = response['Items'] if "Items" in response else []
                while 'LastEvaluatedKey' in response:
                    response = self.__dynamo_client.scan(
                        FilterExpression=Attr('created_by').eq(created_by) & Attr('chat_session_id').eq(
                        chat_session_id) & Attr('created_on').gte(days_limit_str),
                        ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response.get('Items', []))
            elif chat_session_id and not created_by:
                response = self.__dynamo_client.scan(
                    FilterExpression=Attr('chat_session_id').eq(chat_session_id) & Attr('created_on').gte(
                        days_limit_str))
                items = response['Items'] if "Items" in response else []
                while 'LastEvaluatedKey' in response:
                    response = self.__dynamo_client.scan(
                        FilterExpression=Attr('chat_session_id').eq(chat_session_id) & Attr('created_on').gte(
                            days_limit_str),
                        ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response.get('Items', []))
            elif not chat_session_id and created_by:
                response = self.__dynamo_client.scan(
                    FilterExpression=Attr('created_by').eq(created_by) & Attr('created_on').gte(days_limit_str))
                items = response['Items'] if "Items" in response else []
                while 'LastEvaluatedKey' in response:
                    response = self.__dynamo_client.scan(
                        FilterExpression=Attr('created_by').eq(created_by) & Attr('created_on').gte(days_limit_str),
                        ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response.get('Items', []))
            else:
                response = self.__dynamo_client.scan(FilterExpression=Attr('created_on').gte(days_limit_str))
                items = response['Items'] if "Items" in response else []
                return [ChatHistory.from_dict(item) for item in items]
        except Exception as e:
            raise Exception(f"Failed to fetch entries from chat history table. Reason: {e .__str__()}")
            
            
def update_chat_history(self, message_id: str,streaming_data: str) -> bool:
    try:
        logger.info(F"updating streaming answer into chat history. Message_id: {message_id}")
        result = self.__dynamo_client.update_item(
        Key={
        'id': message_id
        },
        UpdateExpression='SET answer = :val',
        ExpressionAttributeValues={
        ':val': streaming_data
        }
        )
        logger.info(f"Updated entry into Chat History, result: {result['ResponseMetadata']['HTTPStatusCode']}")
        return result
    except Exception as e:
        raise Exception(f"Error while updating entry into Chat History Table. Reason: {str(e)}")

def get_raw_data_dashboard(self, start_date: str, end_date: str):
    try:
        response = self.__dynamo_client.scan(
        FilterExpression=Attr('created_on').between(start_date, end_date))
        items = response['Items'] if "Items" in response else []
        return items
    except Exception as e:
        raise Exception(f"Failed to fetch entries from chat history based on start date and end date. Reason: {e .__str__()}")

chat_dto = ChatHistoryDto(boto3.resource(
    'dynamodb',
    region_name=settings.get_aws_region()
    ).Table(settings.get_dynamo_db_table_name_chat_history()))