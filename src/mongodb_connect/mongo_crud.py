"""Backward-compatible adapter for the original mongo_operation API."""

from __future__ import annotations

import warnings
from typing import Any

from mathcyx_mongo_utils import MongoConnection, import_records


class mongo_operation:
    def __init__(
        self,
        client_url: str,
        database_name: str,
        collection_name: str | None = None,
    ) -> None:
        warnings.warn(
            "mongo_operation is deprecated; use MongoConnection and MongoRepository",
            DeprecationWarning,
            stacklevel=2,
        )
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
        self._connection = MongoConnection.from_uri(client_url, database=database_name)
        self.client: Any = None
        self.database: Any = None
        self.collection: Any = None

    def create_mongo_client(self, collection: str | None = None) -> Any:
        del collection
        if self.client is None:
            self.client = self._connection.client
        return self.client

    def create_database(self, collection: str | None = None) -> Any:
        del collection
        if self.database is None:
            self.database = self.create_mongo_client()[self.database_name]
        return self.database

    def create_collection(self, collection: str | None = None) -> Any:
        name = collection or self.collection_name
        if not name:
            raise ValueError("collection_name must be provided")
        if self.collection is None or getattr(self.collection, "name", None) != name:
            self.collection = self.create_database()[name]
        return self.collection

    def insert_record(self, record: Any, collection_name: str) -> Any:
        target = self.create_collection(collection_name)
        if isinstance(record, dict):
            return target.insert_one(record)
        if isinstance(record, list) and all(isinstance(item, dict) for item in record):
            if not record:
                raise ValueError("record list must not be empty")
            return target.insert_many(record)
        raise TypeError("record must be a dictionary or a list of dictionaries")

    def bulk_insert(self, datafile: str, collection_name: str | None = None) -> Any:
        return import_records(datafile, self.create_collection(collection_name))

    def close(self) -> None:
        self._connection.close()
