"""Canonical type vocabulary shared across engines.

Every engine-specific dtype (pandas dtype strings, PySpark DataType names)
is normalized into one of these canonical types before any diffing happens.
This is what makes a pandas-generated lock file valid against a Databricks
Spark table, and vice versa.
"""

CANONICAL_TYPES = {
    "integer",
    "float",
    "string",
    "boolean",
    "timestamp",
    "date",
    "binary",
    "unknown",
}

# Substring markers checked in order against a lowercased raw type name.
# Order matters: more specific markers (e.g. "smallint") must be checked
# before generic ones would otherwise misfire.
_PANDAS_MARKERS = [
    ("bool", "boolean"),
    ("int", "integer"),
    ("float", "float"),
    ("double", "float"),
    ("datetime", "timestamp"),
    ("timestamp", "timestamp"),
    ("date", "date"),
    ("object", "string"),
    ("string", "string"),
    ("str", "string"),
    ("category", "string"),
    ("bytes", "binary"),
]

_SPARK_MARKERS = [
    ("booleantype", "boolean"),
    ("longtype", "integer"),
    ("integertype", "integer"),
    ("shorttype", "integer"),
    ("bytetype", "integer"),
    ("doubletype", "float"),
    ("floattype", "float"),
    ("decimaltype", "float"),
    ("timestamptype", "timestamp"),
    ("datetype", "date"),
    ("stringtype", "string"),
    ("binarytype", "binary"),
]


def normalize(raw_type: str, engine: str) -> str:
    """Map a raw engine-specific type string into the canonical vocabulary.

    engine is either "pandas" or "spark" (or any other engine identifier;
    unrecognized engines fall back to the pandas marker set since most
    Python-facing engines share dtype naming conventions).
    """
    lowered = str(raw_type).lower()

    markers = _SPARK_MARKERS if engine == "spark" else _PANDAS_MARKERS
    for marker, canonical in markers:
        if marker in lowered:
            return canonical

    return "unknown"
