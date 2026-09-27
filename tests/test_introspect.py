from schemalock.introspect import detect_engine, extract_schema
from schemalock.type_map import normalize


def test_detect_engine_pandas(pandas_df):
    assert detect_engine(pandas_df) == "pandas"


def test_detect_engine_unsupported():
    import pytest

    class NotADataFrame:
        pass

    with pytest.raises(TypeError):
        detect_engine(NotADataFrame())


def test_extract_schema_pandas(pandas_df):
    schema = extract_schema(pandas_df)
    assert schema["customer_id"]["type"] == "integer"
    assert schema["email"]["type"] == "string"
    assert schema["signup_ts"]["type"] == "timestamp"
    assert schema["is_active"]["type"] == "boolean"


def test_normalize_pandas_markers():
    assert normalize("int64", "pandas") == "integer"
    assert normalize("float64", "pandas") == "float"
    assert normalize("object", "pandas") == "string"
    assert normalize("bool", "pandas") == "boolean"
    assert normalize("datetime64[ns]", "pandas") == "timestamp"


def test_normalize_spark_markers():
    assert normalize("LongType", "spark") == "integer"
    assert normalize("DoubleType", "spark") == "float"
    assert normalize("StringType", "spark") == "string"
    assert normalize("BooleanType", "spark") == "boolean"
    assert normalize("TimestampType", "spark") == "timestamp"


def test_extract_schema_spark(spark_df):
    schema = extract_schema(spark_df)
    assert schema["customer_id"]["type"] == "integer"
    assert schema["email"]["type"] == "string"
    assert schema["signup_ts"]["type"] == "timestamp"
    assert schema["is_active"]["type"] == "boolean"
