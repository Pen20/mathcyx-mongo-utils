"""MongoDB configuration and connection lifecycle helpers."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


@dataclass(frozen=True, slots=True)
class MongoSettings:
    """Validated settings used to create a MongoDB client."""

    uri: str
    database: str
    app_name: str = "mathcyx-mongo-utils"
    server_selection_timeout_ms: int = 5_000

    def __post_init__(self) -> None:
        if not self.uri.strip():
            raise ValueError("MongoDB URI must not be empty")
        if not self.database.strip():
            raise ValueError("MongoDB database name must not be empty")
        if self.server_selection_timeout_ms <= 0:
            raise ValueError("server_selection_timeout_ms must be positive")

    @classmethod
    def from_env(
        cls,
        *,
        prefix: str = "MONGODB",
        environ: Mapping[str, str] | None = None,
    ) -> MongoSettings:
        values = os.environ if environ is None else environ
        uri_key = f"{prefix}_URI"
        database_key = f"{prefix}_DATABASE"
        try:
            uri = values[uri_key]
            database = values[database_key]
        except KeyError as exc:
            raise ValueError(f"Required environment variable {exc.args[0]} is not set") from exc

        timeout_value = values.get(f"{prefix}_TIMEOUT_MS", "5000")
        try:
            timeout = int(timeout_value)
        except ValueError as exc:
            raise ValueError(f"{prefix}_TIMEOUT_MS must be an integer") from exc

        return cls(
            uri=uri,
            database=database,
            app_name=values.get(f"{prefix}_APP_NAME", "mathcyx-mongo-utils"),
            server_selection_timeout_ms=timeout,
        )


class MongoConnection:
    """Lazy MongoDB client with explicit health checking and shutdown."""

    def __init__(
        self,
        settings: MongoSettings,
        *,
        client_options: Mapping[str, Any] | None = None,
    ) -> None:
        self.settings = settings
        self._client_options = dict(client_options or {})
        self._client: MongoClient[Any] | None = None

    @classmethod
    def from_uri(
        cls,
        uri: str,
        *,
        database: str,
        app_name: str = "mathcyx-mongo-utils",
        server_selection_timeout_ms: int = 5_000,
        client_options: Mapping[str, Any] | None = None,
    ) -> MongoConnection:
        return cls(
            MongoSettings(uri, database, app_name, server_selection_timeout_ms),
            client_options=client_options,
        )

    @property
    def client(self) -> MongoClient[Any]:
        if self._client is None:
            options = {
                "appname": self.settings.app_name,
                "serverSelectionTimeoutMS": self.settings.server_selection_timeout_ms,
                **self._client_options,
            }
            self._client = MongoClient(self.settings.uri, **options)
        return self._client

    @property
    def database(self) -> Database[Any]:
        return self.client[self.settings.database]

    def collection(self, name: str) -> Collection[Any]:
        if not name.strip():
            raise ValueError("Collection name must not be empty")
        return self.database[name]

    def ping(self) -> bool:
        self.client.admin.command("ping")
        return True

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> MongoConnection:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

