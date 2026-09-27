from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from schemalock import lock, check, SchemaDriftError

spark = SparkSession.builder.master("local[1]").appName("schemalock-test").getOrCreate()

schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("email", StringType(), False),
])
df = spark.createDataFrame([(1, "a@x.com"), (2, "b@x.com")], schema)

lock(df, name='demo_spark')  # only if you don't already have a lock file for this name

# 1. drop a column
dropped = df.drop("email")
try:
    check(dropped, name="demo_spark")
except SchemaDriftError as e:
    print(e)

# 2. retype a column (int -> string)
from pyspark.sql.functions import col
retyped = df.withColumn("customer_id", col("customer_id").cast("string"))
try:
    check(retyped, name="demo_spark")
except SchemaDriftError as e:
    print(e)