import sys
from datetime import datetime, timezone

from .errors import LockExistsError, SchemaDriftError
from .introspect import extract_schema
from .serialize import lock_exists, read_lock, write_lock

DEFAULT_DIR = "schemas"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _compute_diff(old_columns: dict, new_columns: dict) -> dict:
    """Diff two {column: {"type", "nullable"}} maps.

    Returns {"missing": [...], "new": [...], "changed": [{"column", "from", "to"}]}.
    "missing" = present in old, absent in new. "new" = present in new, absent in old.
    """
    old_names = set(old_columns)
    new_names = set(new_columns)

    missing = sorted(old_names - new_names)
    added = sorted(new_names - old_names)

    changed = []
    for name in sorted(old_names & new_names):
        old_spec = old_columns[name]
        new_spec = new_columns[name]
        if old_spec != new_spec:
            changed.append({"column": name, "from": old_spec, "to": new_spec})

    return {"missing": missing, "new": added, "changed": changed}


def _diff_is_empty(diff: dict) -> bool:
    return not diff["missing"] and not diff["new"] and not diff["changed"]


def _format_diff(diff: dict) -> str:
    lines = []
    for column in diff["missing"]:
        lines.append(f"  - {column}: removed")
    for column in diff["new"]:
        lines.append(f"  + {column}: added")
    for change in diff["changed"]:
        lines.append(f"  ~ {change['column']}: {change['from']} -> {change['to']}")
    return "\n".join(lines) if lines else "  (no differences)"


def lock(df, name: str, dir: str = DEFAULT_DIR) -> str:
    """Create a new lock file. Errors if one already exists."""
    if lock_exists(name, dir):
        raise LockExistsError(
            f"Lock file already exists for '{name}' in '{dir}'. "
            "Use lock_update() to change an existing lock."
        )
    columns = extract_schema(df)
    return write_lock(name, dir, columns, generated_at=_now(), reason=None)


def check(df, name: str, dir: str = DEFAULT_DIR) -> bool:
    """Validate df's schema against the lock file. Raises SchemaDriftError on mismatch."""
    locked = read_lock(name, dir)
    current_columns = extract_schema(df)
    diff = _compute_diff(locked["columns"], current_columns)

    if not _diff_is_empty(diff):
        raise SchemaDriftError(
            f"Schema drift detected for '{name}':\n{_format_diff(diff)}"
        )
    return True


def lock_update(df, name: str, dir: str = DEFAULT_DIR, reason: str = None) -> str:
    """The only function that can overwrite an existing lock. Interactive confirmation required."""
    if not sys.stdin.isatty():
        raise RuntimeError(
            "lock_update() requires an interactive terminal and cannot run in "
            "CI, scheduled jobs, or other non-interactive automation."
        )

    locked = read_lock(name, dir)
    current_columns = extract_schema(df)
    diff = _compute_diff(locked["columns"], current_columns)

    print(f"Proposed schema changes for '{name}':")
    print(_format_diff(diff))

    if _diff_is_empty(diff):
        print("No differences detected; lock file content is unchanged aside from metadata.")

    typed_name = input(f"Type the schema name ('{name}') to confirm this update: ")
    if typed_name != name:
        raise RuntimeError("Confirmation failed: typed name did not match. Aborting update.")

    if not reason:
        reason = input("Reason for this update (required): ").strip()
    if not reason:
        raise RuntimeError("A non-empty reason is required to update a lock file.")

    return write_lock(name, dir, current_columns, generated_at=_now(), reason=reason)
