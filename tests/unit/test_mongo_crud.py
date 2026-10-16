from unittest.mock import MagicMock, patch

import pytest

from mongodb_connect.mongo_crud import mongo_operation


def test_create_collection_requires_a_name():
    operation = mongo_operation("mongodb://localhost", "test")

    with pytest.raises(ValueError, match="collection_name must be provided"):
        operation.create_collection()


def test_insert_record_rejects_invalid_input():
    operation = mongo_operation("mongodb://localhost", "test", "items")
    operation.collection = MagicMock(name="collection")
    operation.collection.name = "items"

    with pytest.raises(TypeError, match="record must be"):
        operation.insert_record("not a record", "items")


def test_bulk_insert_delegates_to_file_import():
    operation = mongo_operation("mongodb://localhost", "test", "items")
    collection = MagicMock()

    with (
        patch("mongodb_connect.mongo_crud.import_records") as importer,
        patch.object(operation, "create_collection", return_value=collection),
    ):
        operation.bulk_insert("records.csv")

    importer.assert_called_once_with("records.csv", collection)
