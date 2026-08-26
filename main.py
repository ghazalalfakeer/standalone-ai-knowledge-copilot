"""
Main entry point for the Standalone AI Knowledge Copilot.

Task 1 demonstration:

- Read JSON knowledge data
- Validate JSON data
- Add an item
- Update an item
- Delete an item
- Demonstrate missing-file handling
- Demonstrate malformed-JSON handling
- Demonstrate validation-error handling

The original sample_knowledge.json file is never modified.
Modification tests are performed inside a temporary directory.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from src.storage import (
    JsonStorage,
    StorageError,
    StorageItemNotFoundError,
    StorageReadError,
    StorageValidationError,
    validate_knowledge_data,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DATA_FILE = DATA_DIR / "sample_knowledge.json"


def print_separator(title: str) -> None:
    """Print a formatted section separator."""
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def print_knowledge_summary(data: dict[str, Any]) -> None:
    """Print a simple summary of knowledge items."""

    version = data.get("version", "unknown")
    items = data.get("items", [])

    print(f"Knowledge base version: {version}")
    print(f"Number of knowledge items: {len(items)}")
    print()

    for index, item in enumerate(items, start=1):
        title = item.get("title", "Untitled")
        item_id = item.get("id", "unknown")
        tags = item.get("tags", [])

        print(f"{index}. {title}")
        print(f"   ID: {item_id}")
        print(f"   Tags: {', '.join(tags)}")


def demonstrate_read() -> None:
    """Demonstrate reading and validating the sample JSON file."""

    print_separator("1. READ VALID KNOWLEDGE DATA")

    storage = JsonStorage(
        file_path=SAMPLE_DATA_FILE,
        validator=validate_knowledge_data,
    )

    try:
        data = storage.read()

        print(f"Successfully loaded: {SAMPLE_DATA_FILE}")
        print_knowledge_summary(data)

    except StorageError as exc:
        print(f"Storage error: {exc}")


def demonstrate_modifications() -> None:
    """
    Demonstrate JSON modifications.

    A temporary copy of sample_knowledge.json is created so
    that the original project data remains unchanged.
    """

    print_separator("2. ADD, UPDATE AND DELETE KNOWLEDGE ITEMS")

    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_directory_path = Path(temporary_directory)
        demo_file = temporary_directory_path / "knowledge_demo.json"

        shutil.copy2(SAMPLE_DATA_FILE, demo_file)

        storage = JsonStorage(
            file_path=demo_file,
            validator=validate_knowledge_data,
        )

        try:
            print("Created temporary JSON file for modification tests.")

            new_item = {
                "id": "exception-handling",
                "title": "Python Exception Handling",
                "content": (
                    "Python exceptions allow applications to detect "
                    "and handle runtime errors without crashing "
                    "unexpectedly."
                ),
                "tags": [
                    "python",
                    "exceptions",
                    "error-handling",
                ],
                "source": "runtime-demo",
            }

            data = storage.add_item(new_item)

            print()
            print("Added new item:")
            print(new_item["id"])
            print(f"Total items after add: {len(data['items'])}")

            data = storage.update_item(
                item_id="json-storage",
                updates={
                    "title": "JSON Storage in Python",
                    "tags": [
                        "python",
                        "json",
                        "storage",
                        "files",
                    ],
                },
            )

            print()
            print("Updated item:")
            print("json-storage")

            updated_item = next(
                item
                for item in data["items"]
                if item["id"] == "json-storage"
            )

            print(f"New title: {updated_item['title']}")

            data = storage.delete_item(
                item_id="exception-handling"
            )

            print()
            print("Deleted item:")
            print("exception-handling")
            print(f"Total items after delete: {len(data['items'])}")

            final_data = storage.read()

            print()
            print("Final temporary file contents are valid.")
            print_knowledge_summary(final_data)

        except StorageItemNotFoundError as exc:
            print(f"Item not found: {exc}")

        except StorageValidationError as exc:
            print(f"Validation error: {exc}")

        except StorageError as exc:
            print(f"Storage error: {exc}")


def demonstrate_missing_file_error() -> None:
    """Demonstrate error handling when a JSON file does not exist."""

    print_separator("3. MISSING FILE ERROR")

    missing_file = DATA_DIR / "this_file_does_not_exist.json"

    storage = JsonStorage(
        file_path=missing_file,
        validator=validate_knowledge_data,
    )

    try:
        storage.read()

    except StorageReadError as exc:
        print("Expected error was caught successfully:")
        print(exc)


def demonstrate_invalid_json_error() -> None:
    """Demonstrate error handling for malformed JSON syntax."""

    print_separator("4. MALFORMED JSON ERROR")

    with tempfile.TemporaryDirectory() as temporary_directory:
        malformed_file = (
            Path(temporary_directory)
            / "malformed.json"
        )

        malformed_file.write_text(
            """
{
    "version": "1.0",
    "items": [
        {
            "id": "broken-json"
            "title": "This JSON is intentionally invalid"
        }
    ]
}
""".strip(),
            encoding="utf-8",
        )

        storage = JsonStorage(
            file_path=malformed_file,
            validator=validate_knowledge_data,
        )

        try:
            storage.read()

        except StorageReadError as exc:
            print(
                "Expected JSON parsing error was caught successfully:"
            )
            print(exc)


def demonstrate_validation_error() -> None:
    """
    Demonstrate validation of syntactically valid but structurally
    invalid JSON.
    """

    print_separator("5. VALIDATION ERROR")

    invalid_data = {
        "version": "1.0",
        "items": [
            {
                "id": "invalid-item",
                "title": "",
                "content": "This item intentionally has an empty title.",
                "tags": ["demo"],
                "source": "runtime-demo",
            }
        ],
    }

    with tempfile.TemporaryDirectory() as temporary_directory:
        invalid_file = (
            Path(temporary_directory)
            / "invalid_structure.json"
        )

        invalid_file.write_text(
            json.dumps(
                invalid_data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        storage = JsonStorage(
            file_path=invalid_file,
            validator=validate_knowledge_data,
        )

        try:
            storage.read()

        except StorageValidationError as exc:
            print(
                "Expected validation error was caught successfully:"
            )
            print(exc)


def main() -> None:
    """Run all Task 1 demonstrations."""

    print()
    print("Standalone AI Knowledge Copilot")
    print("Task 1 - Python Engineering Foundations")

    demonstrate_read()
    demonstrate_modifications()
    demonstrate_missing_file_error()
    demonstrate_invalid_json_error()
    demonstrate_validation_error()

    print_separator("TASK 1 DEMO COMPLETED")
    print("All demonstrations finished.")


if __name__ == "__main__":
    main()
