"""
Build backend wrapper for maturin that suppresses RUST_LOG to prevent
INFO-level span close events from being printed to stdout after the wheel path,
which would cause maturin's Python wrapper to misidentify the log line as the path.
"""
import os

os.environ.setdefault("RUST_LOG", "warn")
if os.environ.get("RUST_LOG", "warn").lower() == "info":
    os.environ["RUST_LOG"] = "warn"

from maturin import (
    build_editable,
    build_sdist,
    build_wheel,
    get_requires_for_build_editable,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

__all__ = [
    "build_editable",
    "build_sdist",
    "build_wheel",
    "get_requires_for_build_editable",
    "get_requires_for_build_sdist",
    "get_requires_for_build_wheel",
    "prepare_metadata_for_build_editable",
    "prepare_metadata_for_build_wheel",
]
