# app/shared/cosmos_client.py

import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions
from loguru import logger

from app.config import settings

class CosmosDBClient:
    def __init__(self):
        endpoint = settings.get_cosmos_endpoint()
        key = settings.get_cosmos_key()
        if not endpoint or not key:
            raise RuntimeError("CosmosDB endpoint/key not configured.")
        self._client = CosmosClient(endpoint, key)
        self._database_name = settings.get_cosmos_database()
        self._db = None
        self._containers = {}

    async def _get_database(self):
        if self._db is None:
            try:
                self._db = await self._client.create_database_if_not_exists(id=self._database_name)
            except Exception as e:
                logger.error(f"[CosmosDBClient] Error creating database {self._database_name}: {e}")
                raise
        return self._db

    async def _get_container(self, container_name: str, partition_key: str = "/id"):
        if container_name not in self._containers:
            db = await self._get_database()
            try:
                container = await db.create_container_if_not_exists(
                    id=container_name,
                    partition_key=PartitionKey(path=partition_key),
                    offer_throughput=400
                )
                self._containers[container_name] = container
            except Exception as e:
                logger.error(f"[CosmosDBClient] Error creating container {container_name}: {e}")
                raise
        return self._containers[container_name]

    async def upsert_item(self, container_name: str, item: dict, partition_key: str = None):
        container = await self._get_container(container_name)
        return await container.upsert_item(item)

    async def read_item(self, container_name: str, item_id: str, partition_key: str = None):
        container = await self._get_container(container_name)
        try:
            return await container.read_item(item=item_id, partition_key=item_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def query_items(self, container_name: str, query: str, parameters: list = None):
        container = await self._get_container(container_name)
        return container.query_items(query=query, parameters=parameters or [], enable_cross_partition_query=True)

cosmos_client = CosmosDBClient()
