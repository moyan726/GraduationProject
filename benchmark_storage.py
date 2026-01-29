"""
模块名称：存储格式性能基准测试 (CSV vs Parquet)
作者：Trae AI
创建日期：2026-01-29
最后修改：2026-01-29

功能描述：
    对比原始 CSV 格式与分区 Parquet 格式在不同查询场景下的性能差异。
    测试场景包括：全表扫描、单列聚合、条件过滤（分区裁剪）。

输入：
    - data/raw/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019.csv
    - data/dwd/user_behavior (Parquet)

输出：
    - outputs/benchmark/storage_performance.csv
    - outputs/benchmark/benchmark_summary.json

依赖：
    - PySpark 3.5.0
    - Pandas
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    DoubleType,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/benchmark_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_spark_session():
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    os.environ.setdefault("JAVA_HOME", r"E:\Java\jdk1.8.0_291")
    
    return SparkSession.builder \
        .appName("StorageBenchmark") \
        .config("spark.driver.memory", "6g") \
        .getOrCreate()

def run_test(name, func):
    logger.info(f"Running test: {name}...")
    start_time = time.time()
    result = func()
    duration = time.time() - start_time
    logger.info(f"Test {name} completed in {duration:.2f}s (Result: {result})")
    return duration

def main():
    spark = get_spark_session()
    
    csv_path = "data/raw/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019.csv"
    parquet_path = "data/dwd/user_behavior"
    
    if not os.path.exists(csv_path) or not os.path.exists(parquet_path):
        logger.error("Missing input data for benchmark.")
        return

    schema = StructType([
        StructField("event_time", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_id", LongType(), True),
        StructField("category_id", LongType(), True),
        StructField("category_code", StringType(), True),
        StructField("brand", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("user_id", LongType(), True),
        StructField("user_session", StringType(), True),
    ])

    # 1. 加载数据源
    df_csv = spark.read.csv(csv_path, header=True, schema=schema)
    df_parquet = spark.read.parquet(parquet_path)

    results = []

    # --- 场景 1: 全表扫描 Count ---
    results.append({
        "scenario": "Full Scan Count",
        "format": "CSV",
        "duration": run_test("CSV Full Count", lambda: df_csv.count())
    })
    results.append({
        "scenario": "Full Scan Count",
        "format": "Parquet",
        "duration": run_test("Parquet Full Count", lambda: df_parquet.count())
    })

    # --- 场景 2: 单列聚合 Sum(price) ---
    results.append({
        "scenario": "Columnar Sum",
        "format": "CSV",
        "duration": run_test("CSV Sum Price", lambda: df_csv.agg(spark_sum("price")).collect()[0][0])
    })
    results.append({
        "scenario": "Columnar Sum",
        "format": "Parquet",
        "duration": run_test("Parquet Sum Price", lambda: df_parquet.agg(spark_sum("price")).collect()[0][0])
    })

    # --- 场景 3: 条件过滤 (Parquet 分区裁剪) ---
    # 过滤 2019-10-01 的数据
    test_dt = "2019-10-01"
    results.append({
        "scenario": "Filtered Query (dt=2019-10-01)",
        "format": "CSV",
        "duration": run_test("CSV Filtered Count", lambda: df_csv.filter(col("event_time").contains(test_dt)).count())
    })
    results.append({
        "scenario": "Filtered Query (dt=2019-10-01)",
        "format": "Parquet",
        "duration": run_test("Parquet Partition Filtered Count", lambda: df_parquet.filter(col("dt") == test_dt).count())
    })

    # 5. 保存结果
    os.makedirs("outputs/benchmark", exist_ok=True)
    res_df = pd.DataFrame(results)
    res_df.to_csv("outputs/benchmark/storage_performance.csv", index=False, encoding="utf-8-sig")
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "spark_version": spark.version,
        "results": results
    }
    with open("outputs/benchmark/benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("Benchmark completed. Results saved to outputs/benchmark/")
    spark.stop()

if __name__ == "__main__":
    main()
