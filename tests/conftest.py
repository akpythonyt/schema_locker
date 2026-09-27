import shutil

import pytest


@pytest.fixture
def lock_dir(tmp_path):
    d = tmp_path / "schemas"
    yield str(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def pandas_df():
    pandas = pytest.importorskip("pandas")
    return pandas.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "email": ["a@x.com", "b@x.com", "c@x.com"],
            "signup_ts": pandas.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "is_active": [True, False, True],
        }
    )


@pytest.fixture
def spark_session():
    pyspark = pytest.importorskip("pyspark")
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master("local[1]")
        .appName("schemalock-tests")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def spark_df(spark_session):
    from pyspark.sql.types import (
        BooleanType,
        IntegerType,
        StringType,
        StructField,
        StructType,
        TimestampType,
    )
    import datetime

    schema = StructType(
        [
            StructField("customer_id", IntegerType(), False),
            StructField("email", StringType(), False),
            StructField("signup_ts", TimestampType(), False),
            StructField("is_active", BooleanType(), False),
        ]
    )
    rows = [
        (1, "a@x.com", datetime.datetime(2024, 1, 1), True),
        (2, "b@x.com", datetime.datetime(2024, 1, 2), False),
    ]
    return spark_session.createDataFrame(rows, schema)
