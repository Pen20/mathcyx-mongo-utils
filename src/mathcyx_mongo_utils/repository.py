"""Small CRUD wrapper around a PyMongo collection."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from pymongo.collection import Collection
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult


class MongoRepository:
    def __init__(self, collection: Collection[Any]) -> None:
        self.collection = collection

    def insert_one(self, document: Mapping[str, Any]) -> InsertOneResult:
        return self.collection.insert_one(dict(document))

    def insert_many(self, documents: Iterable[Mapping[str, Any]]) -> InsertManyResult:
        materialized = [dict(document) for document in documents]
        if not materialized:
            raise ValueError("documents must contain at least one item")
        return self.collection.insert_many(materialized)

    def find_one(self, query: Mapping[str, Any]) -> dict[str, Any] | None:
        return self.collection.find_one(dict(query))

    def find_many(
        self,
        query: Mapping[str, Any] | None = None,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        if limit is not None and limit < 1:
            raise ValueError("limit must be positive")
        cursor = self.collection.find(dict(query or {}))
        if limit is not None:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_one(
        self,
        query: Mapping[str, Any],
        changes: Mapping[str, Any],
        *,
        upsert: bool = False,
    ) -> UpdateResult:
        update = dict(changes)
        if update and not any(key.startswith("$") for key in update):
            update = {"$set": update}
        if not update:
            raise ValueError("changes must not be empty")
        return self.collection.update_one(dict(query), update, upsert=upsert)

    def delete_one(self, query: Mapping[str, Any]) -> DeleteResult:
        return self.collection.delete_one(dict(query))

