"""
JSON storage utilities for the Standalone AI Knowledge Copilot.

This module provides:

- Safe JSON file reading
- Safe JSON file writing
- Root-level JSON updates
- Adding knowledge items
- Updating knowledge items
- Deleting knowledge items
- Data validation
- Custom exception handling
- Type hints

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, TypeAlias


JsonDict: TypeAlias = dict[str, Any]
Validator: TypeAlias = Callable[[JsonDict], None]


class StorageError(Exception):
    """Base exception for all storage-related errors."""


class StorageReadError(StorageError):
    """Raised when a JSON file cannot be read."""


class StorageWriteError(StorageError):
    """Raised when a JSON file cannot be written."""


class StorageValidationError(StorageError):
    """Raised when JSON data does not satisfy the expected structure."""


class StorageItemNotFoundError(StorageError):
    """Raised when a requested item cannot be found."""


def validate_knowledge_item(item: JsonDict) -> None:
    """
    Validate a single knowledge item.

    Expected structure:

    {
        "id": "unique-id",
        "title": "Title",
        "content": "Knowledge content",
        "tags": ["tag1", "tag2"],
        "source": "optional source"
    }

    Args:
        item: Knowledge item to validate.

    Raises:
        StorageValidationError: If the knowledge item is invalid.
    """

    required_fields = {"id", "title", "content", "tags"}
    missing_fields = required_fields - item.keys()

    if missing_fields:
        raise StorageValidationError(
            "Knowledge item is missing required fields: "
            f"{sorted(missing_fields)}"
        )

    item_id = item["id"]
    if not isinstance(item_id, str) or not item_id.strip():
        raise StorageValidationError("'id' must be a non-empty string.")

    title = item["title"]
    if not isinstance(title, str) or not title.strip():
        raise StorageValidationError(
            f"Item '{item_id}': 'title' must be a non-empty string."
        )

    content = item["content"]
    if not isinstance(content, str) or not content.strip():
        raise StorageValidationError(
            f"Item '{item_id}': 'content' must be a non-empty string."
        )

    tags = item["tags"]
    if not isinstance(tags, list):
        raise StorageValidationError(
            f"Item '{item_id}': 'tags' must be a list."
        )

    if not all(isinstance(tag, str) and tag.strip() for tag in tags):
        raise StorageValidationError(
            f"Item '{item_id}': every tag must be a non-empty string."
        )

    source = item.get("source")
    if source is not None and not isinstance(source, str):
        raise StorageValidationError(
            f"Item '{item_id}': 'source' must be a string or null."
        )


def validate_knowledge_data(data: JsonDict) -> None:
    """
    Validate the complete knowledge-base JSON structure.

    Expected root structure:

    {
        "version": "1.0",
        "items": [...]
    }

    Args:
        data: JSON object to validate.

    Raises:
        StorageValidationError: If the JSON structure is invalid.
    """

    if not isinstance(data, dict):
        raise StorageValidationError("The JSON root must be an object.")

    if "version" not in data:
        raise StorageValidationError(
            "The JSON object must contain a 'version' field."
        )

    version = data["version"]
    if not isinstance(version, str) or not version.strip():
        raise StorageValidationError("'version' must be a non-empty string.")

    if "items" not in data:
        raise StorageValidationError(
            "The JSON object must contain an 'items' field."
        )

    items = data["items"]
    if not isinstance(items, list):
        raise StorageValidationError("'items' must be a list.")

    seen_ids: set[str] = set()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise StorageValidationError(
                f"Item at index {index} must be a JSON object."
            )

        validate_knowledge_item(item)

        item_id = item["id"]
        if item_id in seen_ids:
            raise StorageValidationError(
                f"Duplicate knowledge item ID detected: '{item_id}'."
            )

        seen_ids.add(item_id)


class JsonStorage:
    """
    Manage a JSON file safely.

    The class supports reading, writing, updating, adding,
    editing and deleting JSON-based knowledge items.

    A validation function can optionally be supplied so that
    all data is checked before it is accepted.
    """

    def __init__(
        self,
        file_path: str | Path,
        validator: Validator | None = None,
    ) -> None:
        self.file_path = Path(file_path)
        self.validator = validator

    def read(self) -> JsonDict:
        """Read and validate data from the JSON file."""

        if not self.file_path.exists():
            raise StorageReadError(
                f"JSON file does not exist: {self.file_path}"
            )

        if not self.file_path.is_file():
            raise StorageReadError(
                f"Path is not a file: {self.file_path}"
            )

        try:
            with self.file_path.open(mode="r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise StorageReadError(
                "Invalid JSON syntax in "
                f"'{self.file_path}'. "
                f"Line {exc.lineno}, column {exc.colno}: {exc.msg}"
            ) from exc

        except OSError as exc:
            raise StorageReadError(
                f"Could not read JSON file '{self.file_path}': {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise StorageValidationError("The JSON root must be an object.")

        self._validate(data)
        return data

    def write(self, data: JsonDict) -> None:
        """
        Validate and safely write JSON data using an atomic-write strategy.
        """

        if not isinstance(data, dict):
            raise StorageValidationError(
                "Data passed to write() must be a dictionary."
            )

        self._validate(data)

        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageWriteError(
                f"Could not create directory '{self.file_path.parent}': {exc}"
            ) from exc

        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                json.dump(
                    data,
                    temporary_file,
                    indent=2,
                    ensure_ascii=False,
                )
                temporary_file.write("\n")
                temporary_path = Path(temporary_file.name)

            temporary_path.replace(self.file_path)

        except (OSError, TypeError, ValueError) as exc:
            if temporary_path is not None and temporary_path.exists():
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

            raise StorageWriteError(
                f"Could not write JSON file '{self.file_path}': {exc}"
            ) from exc

    def update(self, updates: Mapping[str, Any]) -> JsonDict:
        """Update root-level fields in the JSON object."""

        if not isinstance(updates, Mapping):
            raise StorageValidationError("updates must be a mapping.")

        data = self.read()
        data.update(dict(updates))
        self.write(data)
        return data

    def add_item(
        self,
        item: JsonDict,
        collection_key: str = "items",
    ) -> JsonDict:
        """Add a new item to a JSON list."""

        if not isinstance(item, dict):
            raise StorageValidationError("The item must be a dictionary.")

        data = self.read()
        items = self._get_collection(
            data=data,
            collection_key=collection_key,
        )

        new_item_id = item.get("id")

        if new_item_id is not None:
            for existing_item in items:
                if (
                    isinstance(existing_item, dict)
                    and existing_item.get("id") == new_item_id
                ):
                    raise StorageValidationError(
                        f"An item with ID '{new_item_id}' already exists."
                    )

        items.append(dict(item))
        self.write(data)
        return data

    def update_item(
        self,
        item_id: str,
        updates: Mapping[str, Any],
        collection_key: str = "items",
    ) -> JsonDict:
        """Update an existing knowledge item by ID."""

        if not isinstance(item_id, str) or not item_id.strip():
            raise StorageValidationError(
                "item_id must be a non-empty string."
            )

        if not isinstance(updates, Mapping):
            raise StorageValidationError("updates must be a mapping.")

        if "id" in updates and updates["id"] != item_id:
            raise StorageValidationError(
                "Changing an existing item's ID is not allowed."
            )

        data = self.read()
        items = self._get_collection(
            data=data,
            collection_key=collection_key,
        )

        for index, existing_item in enumerate(items):
            if not isinstance(existing_item, dict):
                continue

            if existing_item.get("id") == item_id:
                updated_item = {
                    **existing_item,
                    **dict(updates),
                }

                items[index] = updated_item
                self.write(data)
                return data

        raise StorageItemNotFoundError(
            f"Item with ID '{item_id}' was not found."
        )

    def delete_item(
        self,
        item_id: str,
        collection_key: str = "items",
    ) -> JsonDict:
        """Delete an item by ID."""

        if not isinstance(item_id, str) or not item_id.strip():
            raise StorageValidationError(
                "item_id must be a non-empty string."
            )

        data = self.read()
        items = self._get_collection(
            data=data,
            collection_key=collection_key,
        )

        for index, existing_item in enumerate(items):
            if not isinstance(existing_item, dict):
                continue

            if existing_item.get("id") == item_id:
                del items[index]
                self.write(data)
                return data

        raise StorageItemNotFoundError(
            f"Item with ID '{item_id}' was not found."
        )

    def _validate(self, data: JsonDict) -> None:
        """Run the configured validation function."""

        if self.validator is not None:
            self.validator(data)

    @staticmethod
    def _get_collection(
        data: JsonDict,
        collection_key: str,
    ) -> list[Any]:
        """Return a list collection from the JSON object."""

        if not isinstance(collection_key, str) or not collection_key.strip():
            raise StorageValidationError(
                "collection_key must be a non-empty string."
            )

        if collection_key not in data:
            raise StorageValidationError(
                f"Collection '{collection_key}' does not exist."
            )

        collection = data[collection_key]

        if not isinstance(collection, list):
            raise StorageValidationError(
                f"'{collection_key}' must be a list."
            )

        return collection
