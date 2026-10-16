"""Load records from common files and insert them into MongoDB."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, cast

from pymongo.collection import Collection
from pymongo.results import InsertManyResult


def read_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    suffix = source.suffix.lower()

    if suffix == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            return [dict(row) for row in csv.DictReader(stream)]
    if suffix == ".json":
        with source.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError("JSON input must be an array of objects")
        return cast(list[dict[str, Any]], data)
    if suffix in {".jsonl", ".ndjson"}:
        with source.open("r", encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("JSON Lines input must contain one object per line")
        return cast(list[dict[str, Any]], rows)
    if suffix in {".xlsx", ".xls"}:
        try:
            import pandas as pd  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "Excel support requires: pip install 'mathcyx-mongo-utils[data]'"
            ) from exc
        records = pd.read_excel(source).to_dict(orient="records")
        return cast(list[dict[str, Any]], records)

    raise ValueError("Supported file types are .csv, .json, .jsonl, .ndjson, .xlsx, and .xls")


def import_records(path: str | Path, collection: Collection[Any]) -> InsertManyResult:
    records = read_records(path)
    if not records:
        raise ValueError("Input file contains no records")
    return collection.insert_many(records)

