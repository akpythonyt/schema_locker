from schemalock import check, lock


def test_pandas_lock_then_spark_check(pandas_df, spark_df, lock_dir):
    lock(pandas_df, name="customer_silver", dir=lock_dir)
    assert check(spark_df, name="customer_silver", dir=lock_dir) is True


def test_spark_lock_then_pandas_check(pandas_df, spark_df, lock_dir):
    lock(spark_df, name="customer_silver", dir=lock_dir)
    assert check(pandas_df, name="customer_silver", dir=lock_dir) is True
