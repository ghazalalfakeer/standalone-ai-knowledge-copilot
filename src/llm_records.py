"""Persistence helpers for Task 3 LLM run evidence."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROJECT_ROOT
from src.llm_client import LLMRunResult

DEFAULT_RUN_DIRECTORY = PROJECT_ROOT / "artifacts" / "llm_runs"


def save_llm_run(
    result: LLMRunResult,
    output_directory: str | Path = DEFAULT_RUN_DIRECTORY,
) -> Path:
    """Save one LLM run as formatted JSON using an atomic file replacement."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    final_path = directory / f"llm_run_{timestamp}.json"
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            prefix=".llm_run_",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            json.dump(
                result.to_dict(),
                temporary_file,
                indent=2,
                ensure_ascii=False,
            )
            temporary_file.write("\n")
            temporary_path = Path(temporary_file.name)

        temporary_path.replace(final_path)
        return final_path

    except (OSError, TypeError, ValueError):
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                pass
        raise
