# REES46 电商行为数据字典（Track A：2019-10）

数据来源：`data/raw/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019.csv`（本地文件）  
样本范围：2019-10（由 `data/dwd/sample_oct_2019` 过滤生成）  
基础统计输出：`outputs/eda/summary.json`、`outputs/eda/missing_rates.csv`、`outputs/eda/event_type_counts.csv`

## 字段定义

| 字段名 | 建议类型 | 业务含义 | 取值/示例 | 备注 |
|---|---|---|---|---|
| `event_time` | string / timestamp | 事件发生时间（UTC） | `2019-10-01T00:00:00.000Z` | 建议在 DWD 转换为 `timestamp` 并派生 `dt` 分区 |
| `event_type` | string | 行为类型 | `view` / `cart` / `purchase` / `remove_from_cart` | Track A(2019-10) 统计到 `view/cart/purchase` |
| `product_id` | long | 商品 ID | `1003461` | 主分析维度之一 |
| `category_id` | long | 类目 ID | `2053013555631882655` | 与 `category_code` 并存 |
| `category_code` | string | 类目层级编码 | `electronics.smartphone` | 缺失较高，需单独分析其业务影响 |
| `brand` | string | 品牌 | `xiaomi` | 缺失较高，需单独分析其业务影响 |
| `price` | double | 价格 | `489.07` | 建议额外做 `price <= 0` 异常审计 |
| `user_id` | long | 用户 ID | `520088904` | 用于 UV、RFM 等 |
| `user_session` | string | 会话 ID（UUID） | `4d3b30da-a5e4-...` | 可用于 Session 漏斗口径 |

## Track A 质量审计结论（2019-10）

### 规模与去重（近似）

- 总事件数：42112054
- 近似独立用户数（`user_id`）：3134159
- 近似独立会话数（`user_session`）：8819313

### 行为分布（Top）

- `view`：40449653
- `cart`：923354
- `purchase`：739047

### 缺失值分布（Top）

- `category_code`：缺失率约 31.83%
- `brand`：缺失率约 14.39%
- `user_session`：极少量缺失（接近 0）

## 清洗与口径建议（第一阶段输出）

### 缺失值（强制记录策略）

- DWD 层：建议保真保留 `NULL`，不在 DWD 强行填充为 `"unknown"`
- ADS/BI 层：若展示或聚合需要，可在视图层将 `NULL` 映射为 `"unknown"`，并同时保留原始缺失统计

### 异常值（建议审计策略）

- `price <= 0`：优先审计其占比与来源，再决定剔除/保留/标记
- 极端高价：建议以分位数（如 P99.9）做截尾或 `is_outlier` 标记，避免平均值被极端值拉偏

### Session 口径（建议复用源端字段）

- 以 `user_session` 作为一次访问会话标识，优先复用源端 `user_session`，避免在第一阶段引入复杂的二次会话化逻辑
