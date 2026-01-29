"""
模块名称：Serving 层导出脚本 (Export to Serving)
作者：Trae AI
创建日期：2026-01-29

功能描述：
    1. 读取 ADS 层的所有分析结果。
    2. 导出为 CSV 格式供 Power BI 直接读取。
    3. 提供 MySQL 导出代码模版。

输入：
    - data/ads/
输出：
    - data/serving/*.csv
"""

import os
import sys
import logging
from datetime import datetime
from pyspark.sql import SparkSession

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/export_serving_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_spark_session():
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    os.environ.setdefault("JAVA_HOME", r"E:\Java\jdk1.8.0_291")
    
    return SparkSession.builder \
        .appName("Export_To_Serving") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

def export_to_csv(df, name):
    output_dir = f"data/serving/{name}"
    logger.info(f"Exporting {name} to CSV...")
    # 合并为一个文件导出方便 Power BI 读取
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_dir)
    logger.info(f"Successfully exported {name} to {output_dir}")

def main():
    spark = get_spark_session()
    
    # 定义需要导出的表
    tables = {
        "funnel_stats": "data/ads/ads_funnel_stats",
        "user_retention": "data/ads/ads_user_retention",
        "user_rfm": "data/ads/ads_user_rfm",
        "user_clusters": "data/ads/ads_user_clusters"
    }

    for name, path in tables.items():
        if os.path.exists(path):
            df = spark.read.parquet(path)
            
            # 1. 导出为 CSV (Power BI 常用)
            export_to_csv(df, name)
            
            # 2. MySQL 导出模版 (如果需要使用，请取消注释并配置参数)
            """
            logger.info(f"Exporting {name} to MySQL...")
            df.write.format("jdbc") \
                .option("url", "jdbc:mysql://localhost:3306/graduation_db?useSSL=false") \
                .option("dbtable", f"ads_{name}") \
                .option("user", "root") \
                .option("password", "your_password") \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .mode("overwrite") \
                .save()
            """
        else:
            logger.warning(f"Path not found, skipping: {path}")

    logger.info("All serving data exported.")
    spark.stop()

if __name__ == "__main__":
    main()
