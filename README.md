# 基于 PySpark 的电商行为数据分析 (毕业设计)

本项目旨在利用 PySpark 对大规模电商行为数据进行清洗、建模与分析，并最终实现可视化展示。

## 📊 当前进度
- **第一阶段 (数据理解)**: ✅ 已完成。产出 EDA 报告、数据字典。
- **第二阶段 (ETL 与存储优化)**: ✅ 已完成。建立 DWD 层分区表，完成存储性能对比。
- **第三阶段 (核心分析模块)**: 🚀 已完成。实现转化漏斗、留存分析及 RFM 用户分层。

## 🛠️ 环境要求
- Python 3.11+
- JDK 1.8 (会话级配置)
- Conda 环境: `graduation_project`
- 运行规范见: [ENVIRONMENT.md](docs/guides/ENVIRONMENT.md)

## 📂 目录结构
- `docs/`: 包含架构设计、编码标准、实验日志及里程碑清单。
- `data/`: 数据分层目录 (ODS/DWD/DWS/ADS)。
- `outputs/`: 脚本输出的 CSV、JSON 结果及图表。
- `scripts/`: 开发辅助脚本（如 `dev_shell.ps1`）。

## 🚀 核心脚本
1. `etl_dwd_user_behavior.py`: DWD 明细层清洗。
2. `benchmark_storage.py`: 存储格式性能基准测试。
3. `eda_oct_2019.py`: 10 月数据探索性分析。

## 📜 规则与约束
所有开发必须遵守 [PROJECT_RULES.md](docs/rules/PROJECT_RULES.md) 中的环境隔离原则。
