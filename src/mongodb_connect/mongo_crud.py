import json
from typing import Any, Optional

import pandas as pd
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


class mongo_operation:
    def __init__(
        self, client_url: str, database_name: str, collection_name: Optional[str] = None
    ) -> None:
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None

    def create_mongo_client(self, collection: Optional[str] = None) -> MongoClient:
        del collection  # Retained for compatibility with the original public API.
        if self.client is None:
            self.client = MongoClient(self.client_url)
        return self.client

    def create_database(self, collection: Optional[str] = None) -> Database:
        if self.database is None:
            self.database = self.create_mongo_client(collection)[self.database_name]
        return self.database

    def create_collection(self, collection: Optional[str] = None) -> Collection:
        collection_name = collection or self.collection_name
        if not collection_name:
            raise ValueError("collection_name must be provided")
        if self.collection is None or self.collection.name != collection_name:
            self.collection = self.create_database(collection_name)[collection_name]
        return self.collection

    def insert_record(self, record: Any, collection_name: str) -> Any:
        collection = self.create_collection(collection_name)
        if isinstance(record, list):
            if not all(isinstance(data, dict) for data in record):
                raise TypeError("every record must be a dictionary")
            return collection.insert_many(record)
        if isinstance(record, dict):
            return collection.insert_one(record)
        raise TypeError("record must be a dictionary or a list of dictionaries")

    def bulk_insert(self, datafile: str, collection_name: Optional[str] = None) -> Any:
        if datafile.endswith(".csv"):
            dataframe = pd.read_csv(datafile, encoding="utf-8")
        elif datafile.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile)
        else:
            raise ValueError("datafile must be a .csv or .xlsx file")

        datajson = json.loads(dataframe.to_json(orient="records"))
        return self.create_collection(collection_name).insert_many(datajson)
