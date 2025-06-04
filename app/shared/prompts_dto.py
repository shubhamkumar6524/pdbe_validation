import json
import uuid
from datetime import datetime

import boto3
from loguru import logger

from app.config import settings

class PromptsDto:

    def __init__(self, client) -> None:
        self.__dynamo_client = client

    def update_prompts(self, prompts: dict, created_by):
        try:
            logger.info(f"Updating Prompts into the table, prompts:(prompts), created_by:(created_by]")
            prompts_obj = self.get_prompts()
            prompts_obj=self.__update_prompts(prompts_obj if prompts_obj else {}, prompts)
            result = self.__dynamo_client.put_item(Item={
            "id": str(uuid.uuid4()),
            "created_on": datetime.now().strftime("XY-Xm-Xd_XH-XM-XS"),
            "created_by": created_by,
            "prompt": prompts_obj
            })
            logger.info(f"Updated entry into the prompt table. result: {result['ResponseMetadata']['HTTPStatusCode']}")
            return True
        except Exception as e:
            raise Exception(f"Error while inserting entry into prompts table. Reason: {str(e)}")
        
    def get_prompts(self):
        try:
            logger.info(f"Fetching entry from prompt table.")
            response = self.__dynamo_client.scan() # Use scan if you don't have a specific key to query
            items = response['Items']
            if items:
                latest_item = max(items, key=lambda x: x['created_on'])
                return latest_item['prompt']
            else:
                return None
        except Exception as e:
            raise Exception(f"Error while fetching prompts from prompts table. Reason: {str(e)}")
        
    def __update_prompts(self, prompts_obj: dict, prompts_dict: dict): 
        list_prompts = ['chat_generate_standalone_system', 'chat_summarization_system', 'chat_summarization_user', 'chat_system', 'chat_user', 'chat_tabular_format'
        'trending_questions_system', 'trending_questions_user', 'chat_citation_user_prompt', 'chat_citation_system_prompt']
        for prompt in list_prompts:
            self.__update_prompts_key(prompts_obj, prompts_dict, prompt)
        return prompts_obj

    def __update_prompts_key(self, prompts_obj: dict, prompts_dict: dict, key: str):
        if key in prompts_dict.keys():
            logger.info(f"Updating (key) with old_value:{prompts_obj.get(key, None)},new_value:{prompts_dict.get(key, None)}")
            prompts_obj[key]= prompts_dict.get(key, None)

    def get_prompts_text(self,prompts,prompt_dict, key):
        if prompts:
            prompts= prompts.file.read()
            prompt_dict[key]=prompts.decode('utf-8')
        return prompt_dict

prompts_dto = PromptsDto(boto3.resource(
'dynamodb',
region_name=settings.get_aws_region()
).Table(settings.get_dynamo_db_table_name_prompt()))
            