"""
模块名称：性能优化实验 - 数据倾斜治理 (加盐聚合演示)
作者：Trae AI
创建日期：2026-01-29

功能描述：
    对比普通聚合与加盐聚合在处理倾斜数据时的性能差异。
    使用 brand 维度进行聚合演示。

输入：
    - data/dwd/user_behavior
"""

import os
import sys
import time
import logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, concat, lit, rand, split

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/perf_skew_optimization_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_spark_session():
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    os.environ.setdefault("JAVA_HOME", r"E:\Java\jdk1.8.0_291")
    
    return SparkSession.builder \
        .appName("Perf_Skew_Optimization") \
        .config("spark.driver.memory", "6g") \
        .config("spark.sql.shuffle.partitions", "20") \
        .getOrCreate()

def main():
    spark = get_spark_session()
    df_dwd = spark.read.parquet("data/dwd/user_behavior")

    # 1. 场景 A: 普通聚合 (可能产生倾斜)
    logger.info("Starting Scenario A: Normal Aggregation...")
    start_a = time.time()
    res_normal = df_dwd.groupBy("brand").agg(count("*").alias("cnt"))
    res_normal.collect() # 触发计算
    duration_a = time.time() - start_a
    logger.info(f"Normal Aggregation duration: {duration_a:.2f}s")

    # 2. 场景 B: 两阶段加盐聚合
    logger.info("Starting Scenario B: Two-Stage Salting Aggregation...")
    start_b = time.time()
    
    # 第一阶段：局部聚合 (加盐)
    salt_range = 10
    df_salted = df_dwd.withColumn("salt", (rand() * salt_range).cast("int")) \
                      .withColumn("salted_key", concat(col("brand"), lit("_"), col("salt")))
    
    partial_agg = df_salted.groupBy("salted_key").agg(count("*").alias("partial_cnt"))
    
    # 第二阶段：全局聚合 (去盐)
    final_agg = partial_agg.withColumn("original_key", split(col("salted_key"), "_")[0]) \
                           .groupBy("original_key").agg({"partial_cnt": "sum"})
    
    final_agg.collect() # 触发计算
    duration_b = time.time() - start_b
    logger.info(f"Salting Aggregation duration: {duration_b:.2f}s")

    # 3. 记录结果
    logger.info(f"Optimization Summary: Normal={duration_a:.2f}s, Salted={duration_b:.2f}s")
    
    spark.stop()

if __name__ == "__main__":
    main()
