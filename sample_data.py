"""
模块名称：数据采样与格式转换
作者：[待填]
创建日期：2026-01-29
最后修改：2026-01-29

功能描述：
    从原始 CSV 数据中按月份过滤数据，并保存为 Parquet（Track A 样本）。

输入：
    - data/raw/*.csv（默认：data/raw/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019.csv）

输出：
    - data/dwd/sample_oct_2019（Parquet 目录）
    - logs/sample_data_<YYYYMMDD>.log

依赖：
    - PySpark 3.5.0
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType, LongType, StringType, StructField, StructType


def setup_logger(script_name: str) -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/{script_name}_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )
    return logging.getLogger(script_name)


def build_schema() -> StructType:
    return StructType(
        [
            StructField("event_time", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("product_id", LongType(), True),
            StructField("category_id", LongType(), True),
            StructField("category_code", StringType(), True),
            StructField("brand", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("user_id", LongType(), True),
            StructField("user_session", StringType(), True),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="按月份抽取 REES46 数据并转为 Parquet（Track A）")
    parser.add_argument(
        "--input",
        default="data/raw/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019.csv",
        help="输入 CSV 路径（相对项目根目录）",
    )
    parser.add_argument(
        "--output",
        default="data/dwd/sample_oct_2019",
        help="输出 Parquet 目录（相对项目根目录）",
    )
    parser.add_argument("--month", default="2019-10", help="过滤月份，格式 YYYY-MM（例如 2019-10）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = setup_logger("sample_data")

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    os.environ.setdefault("JAVA_HOME", r"E:\Java\jdk1.8.0_291")

    project_root = Path(__file__).resolve().parent
    input_path = (project_root / args.input).as_posix()
    output_dir = (project_root / args.output).as_posix()

    logger.info("PYSPARK_PYTHON=%s", os.environ.get("PYSPARK_PYTHON"))
    logger.info("JAVA_HOME=%s", os.environ.get("JAVA_HOME"))
    logger.info("Input CSV=%s", input_path)
    logger.info("Output Parquet=%s", output_dir)
    logger.info("Filter month=%s", args.month)

    spark = (
        SparkSession.builder.appName("DataSampling")
        .config("spark.driver.memory", "4g")
        .config("spark.executor.memory", "4g")
        .getOrCreate()
    )

    schema = build_schema()
    df = spark.read.csv(input_path, header=True, schema=schema)

    month_prefix = args.month
    df_month = df.filter(col("event_time").startswith(month_prefix))

    df_month.write.mode("overwrite").parquet(output_dir)
    logger.info("Sampling completed.")

    spark.stop()


if __name__ == "__main__":
    main()
