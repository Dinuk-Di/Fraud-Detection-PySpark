import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType

spark = SparkSession.builder.appName("PySparkU").getOrCreate()

schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("value", IntegerType(), True)
])

data = [(i,i*2) for i in range(100)]

df = spark.createDataFrame(data, schema)

df.show()

spark.stop()