import json
from unittest.mock import MagicMock, patch

import pytest

from mathcyx_mongo_utils import (
    MongoConnection,
    MongoRepository,
    MongoSettings,
    import_records,
    read_records,
)


def test_settings_load_from_environment():
    settings = MongoSettings.from_env(
        environ={
            "MONGODB_URI": "mongodb://example",
            "MONGODB_DATABASE": "application",
            "MONGODB_TIMEOUT_MS": "1200",
        }
    )

    assert settings.database == "application"
    assert settings.server_selection_timeout_ms == 1200


def test_settings_report_missing_variable():
    with pytest.raises(ValueError, match="MONGODB_DATABASE"):
        MongoSettings.from_env(environ={"MONGODB_URI": "mongodb://example"})


@patch("mathcyx_mongo_utils.connection.MongoClient")
def test_connection_is_lazy_and_closes(mock_client_class):
    client = MagicMock()
    mock_client_class.return_value = client
    connection = MongoConnection.from_uri("mongodb://example", database="application")

    mock_client_class.assert_not_called()
    assert connection.ping() is True
    mock_client_class.assert_called_once()
    client.admin.command.assert_called_once_with("ping")

    connection.close()
    client.close.assert_called_once()


def test_repository_wraps_plain_updates_in_set():
    collection = MagicMock()
    repository = MongoRepository(collection)

    repository.update_one({"email": "a@example.org"}, {"active": False})

    collection.update_one.assert_called_once_with(
        {"email": "a@example.org"},
        {"$set": {"active": False}},
        upsert=False,
    )


def test_repository_rejects_empty_bulk_insert():
    with pytest.raises(ValueError, match="at least one"):
        MongoRepository(MagicMock()).insert_many([])


def test_read_records_supports_json_and_json_lines(tmp_path):
    json_path = tmp_path / "records.json"
    json_path.write_text(json.dumps([{"name": "Ada"}]), encoding="utf-8")
    jsonl_path = tmp_path / "records.jsonl"
    jsonl_path.write_text('{"name": "Ada"}\n{"name": "Grace"}\n', encoding="utf-8")

    assert read_records(json_path) == [{"name": "Ada"}]
    assert read_records(jsonl_path) == [{"name": "Ada"}, {"name": "Grace"}]


def test_import_records_rejects_empty_file(tmp_path):
    csv_path = tmp_path / "records.csv"
    csv_path.write_text("name\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no records"):
        import_records(csv_path, MagicMock())

