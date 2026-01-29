import os
import sys
from pyspark.sql import SparkSession

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
os.environ.setdefault("JAVA_HOME", r"E:\Java\jdk1.8.0_291")

spark = SparkSession.builder.appName("Verify_ADS").getOrCreate()

print("--- Funnel Summary ---")
df_funnel = spark.read.parquet("data/ads/ads_funnel_stats")
df_funnel.filter("dimension = 'global'").show()

print("--- Retention Sample (First 5 Cohorts, period 0 & 1) ---")
df_ret = spark.read.parquet("data/ads/ads_user_retention")
df_ret.filter("period <= 1").orderBy("cohort_date", "period").show(10)

print("--- RFM Segmentation Summary ---")
df_rfm = spark.read.parquet("data/ads/ads_user_rfm")
df_rfm.groupBy("rfm_segment").count().show()

spark.stop()
