"""Engine detection and schema extraction.

Detection is based on type(df).__module__ prefix, never isinstance — this
keeps schemalock free of hard dependencies on pandas or pyspark, since it
never needs to import their classes to recognize a dataframe.

Core logic never branches on "what environment am I in" (e.g. Databricks
vs. local Spark); it only ever inspects the dataframe object handed to it.
"""

from .type_map import normalize


def detect_engine(df) -> str:
    module = type(df).__module__
    if module.startswith("pandas"):
        return "pandas"
    if module.startswith("pyspark"):
        return "spark"
    raise TypeError(
        f"Unsupported dataframe type: {type(df)!r} (module {module!r}). "
        "schemalock supports pandas and pyspark DataFrames."
    )


def extract_schema(df) -> dict:
    """Return {column_name: {"type": canonical_type, "nullable": bool}}."""
    engine = detect_engine(df)
    if engine == "pandas":
        return _extract_pandas(df)
    return _extract_spark(df)


def _extract_pandas(df) -> dict:
    schema = {}
    for column in df.columns:
        dtype = df[column].dtype
        nullable = bool(df[column].isnull().any())
        schema[str(column)] = {
            "type": normalize(str(dtype), engine="pandas"),
            "nullable": nullable,
        }
    return schema


def _extract_spark(df) -> dict:
    schema = {}
    for field in df.schema.fields:
        schema[field.name] = {
            "type": normalize(type(field.dataType).__name__, engine="spark"),
            "nullable": bool(field.nullable),
        }
    return schema
