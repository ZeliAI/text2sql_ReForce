# dws_hk_asap_mkt_distribute_index_1d
> 返回 [投放域总览](./投放域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | odps.sg.anthk_sg.dws_hk_asap_mkt_distribute_index_1d |
| 层级 | DWS（汇总层） |
| 描述 | 投放曝光点击轻度汇总表 |
| 数据范围 | 投放域（首页feeds / 腰封 / 支付结果页 / 投放任务） |
| 主键 | - |
| 外键 | space_id → dim_hk_asap_space_info_dd |
| 外键 | content_id → dim_hk_asap_content_dd |
| 外键 | industry_org_id → dim_hk_asap_industry_info_dd |
| 分区 | dt（格式：yyyyMMdd，如 20260319） |

> ⚠️ **选表说明**：本表为 DWS 层，查询曝光/点击 PV 等基础指标时**优先使用本表**，避免扫描 DWD 明细日志。仅当需要用户行为明细时，才降级使用 DWD 层。

---

## 二、核心字段列表
### 2.1 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| dt | string | 日期分区 | 格式: yyyyMMdd，如 "20260319" | 高 |
| space_id | string | 展位ID | 外键→dim_hk_asap_space_info_dd | 高 |
| space_code | string | 展位CODE | 如 "HK_HOME_PAGE_THEME_BANNER" | 高 |
| space_name | string | 展位名称 | 如 "首页feeds" | 高 |
| delivery_task_id | string | 投放任务ID | 外键→dim_hk_asap_mkt_delivery_task_dd | 高 |
| delivery_task_name | string | 投放任务名称 | 举例： "12.29-生活频道-北上-$90" | 高 |
| industry_org_id | string | 行业ID | 外键→dim_hk_asap_industry_info_dd | 高 |
| industry_org_name | string | 行业名称 | 数字生活_积分, 数字金融_自营金融, 数字支付_交通等 | 高 |
| content_id | string | 投放内容ID / 供给ID / 商户ID | 举例：sgprodsg_maga_hktraffic_static_content... | 高 |
| title | string | 投放内容标题 / 供给名称 / 商户名称 | 举例：流失電訊用戶首頁卡片 | 高 |
| content_type | string | 内容类型 | STATIC_CONTENT, POINT_TASK, BENEFIT, SALE_BENEFIT, EXCHANGE, BRAND, TICKET, MINI_APP, SIM | 高 |
| traffic_type | string | 流量类型 | NON_COMMERCIAL_COMPETITIVE(竞争流量), COMMERCIAL(商业化流量), NON_COMMERCIAL_BUDGET(预算流量) | 高 |
| user_id | string | 用户ID（计算UV时使用） | 举例：2088000341822826 | 高 |
| slot_id | int | 坑位ID | 1, 2, 3, 4, 5, 6, 7, 8 | 中 |
| is_public | tinyint | 是否公域展位 | 1（公域）/ 0（非公域） | 中 |
| delivery_task_status | string | 投放任务状态 | RELEASED | 中 |
| environment | string | 环境标识 | R: Released（线上）/ P: Pre（预发），线上查询必须过滤 environment = 'R' | 低 |

### 2.2 指标字段
| 字段名 | 类型 | 描述 | 使用方式 | 热度 |
| --- | --- | --- | --- | --- |
| expo_pv_1d | bigint | 曝光PV / 流量消耗 | 预存字段，直接 SUM(expo_pv_1d) | 高 |
| clk_pv_1d | bigint | 点击PV | 预存字段，直接 SUM(clk_pv_1d) | 高 |
| expo_uv（计算指标） | - | 曝光UV | COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END) | 高 |
| clk_uv（计算指标） | - | 点击UV | COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END) | 高 |
| pv_ctr（计算指标） | - | PV点击率 | SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0) | 高 |
| uv_ctr（计算指标） | - | UV点击率 | clk_uv / NULLIF(expo_uv, 0) | 高 |

---

## 三、业务术语映射（NL2SQL 关键）
### 3.1 流量类型 / 展位类型
| 用户说的 | 技术含义 | 对应写法 |
| --- | --- | --- |
| 竞争流量 | traffic_type = 'NON_COMMERCIAL_COMPETITIVE' | WHERE traffic_type = 'NON_COMMERCIAL_COMPETITIVE' |
| 商业化流量 | traffic_type = 'COMMERCIAL' | WHERE traffic_type = 'COMMERCIAL' |
| 预算流量 | traffic_type = 'NON_COMMERCIAL_BUDGET' | WHERE traffic_type = 'NON_COMMERCIAL_BUDGET' |
| 公域展位 | is_public = 1 | WHERE is_public = 1 |
| 非公域展位 | is_public = 0 | WHERE is_public = 0 |
| 2号坑位 / 第2个位置 | slot_id = 2 | WHERE slot_id = 2 |

---

## 四、常用查询场景
### 4.1 查询展位曝光/点击 PV（优先走 DWS）
```sql
SELECT
    space_name,
    SUM(expo_pv_1d) AS expo_pv,
    SUM(clk_pv_1d) AS clk_pv,
    ROUND(SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0), 4) AS pv_ctr
FROM dws_hk_asap_mkt_distribute_index_1d
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY space_name
ORDER BY expo_pv DESC
```

### 4.2 计算曝光UV / 点击UV / UV CTR
```sql
SELECT
    space_name,
    SUM(expo_pv_1d) AS expo_pv,
    SUM(clk_pv_1d) AS clk_pv,
    COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END) AS expo_uv,
    COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END) AS clk_uv,
    ROUND(
        COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END)
        / NULLIF(COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END), 0)
    , 4) AS uv_ctr
FROM dws_hk_asap_mkt_distribute_index_1d
WHERE dt = '${bizdate}'
  AND space_name = '首页feeds'
  AND environment = 'R'
GROUP BY space_name
```

### 4.3 最近 N 天趋势查询
```sql
SELECT
    dt,
    SUM(expo_pv_1d) AS expo_pv,
    SUM(clk_pv_1d) AS clk_pv,
    ROUND(SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0), 4) AS pv_ctr
FROM dws_hk_asap_mkt_distribute_index_1d
WHERE dt >= DATE_FORMAT(DATE_SUB('${bizdate}', 6), 'yyyyMMdd')
  AND dt <= '${bizdate}'
  AND space_name = '首页feeds'
  AND environment = 'R'
GROUP BY dt
ORDER BY dt
```

### 4.4 竞争流量消耗统计
```sql
SELECT
    space_name,
    SUM(expo_pv_1d) AS compete_expo_pv
FROM dws_hk_asap_mkt_distribute_index_1d
WHERE dt = '${bizdate}'
  AND traffic_type = 'NON_COMMERCIAL_COMPETITIVE'
  AND environment = 'R'
GROUP BY space_name
ORDER BY compete_expo_pv DESC
```

### 4.5 公域展位指定坑位 UV CTR TOP 内容
```sql
SELECT
    content_id,
    title,
    COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END) AS expo_uv,
    COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END) AS clk_uv,
    ROUND(
        COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END)
        / NULLIF(COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END), 0)
    , 4) AS uv_ctr
FROM dws_hk_asap_mkt_distribute_index_1d
WHERE dt >= DATE_FORMAT(DATE_SUB('${bizdate}', 6), 'yyyyMMdd')
  AND dt <= '${bizdate}'
  AND is_public = 1
  AND slot_id = 2
  AND environment = 'R'
GROUP BY content_id, title
ORDER BY uv_ctr DESC
LIMIT 1
```

### 4.6 大盘整体 PV/UV
```sql
SELECT
    SUM(expo_pv_1d) AS total_expo_pv,
    SUM(clk_pv_1d) AS total_clk_pv,
    COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END) AS total_expo_uv
FROM dws_hk_asap_mkt_distribute_index_1d
WHERE dt = '${bizdate}'
  AND environment = 'R'
```

---

## 五、注意事项
1. **分区字段**：dt 为分区字段，查询时必须指定，格式为 yyyyMMdd（如 20260319）
2. **环境过滤**：线上数据查询时必须加 environment = 'R'，过滤预发数据
3. **指标读取**：expo_pv_1d、clk_pv_1d 是预存字段，直接 SUM 即可；UV 和 CTR 需通过 user_id 配合 COUNT DISTINCT 计算
4. **DWS 优先**：查曝光 PV、点击 PV、PV CTR 等指标优先走本表；只有需要更细粒度明细时才降级到 DWD
5. **展位名称转换**：用户口语描述（如"腰封"、"支付结果页"）需转换为实际 space_name，详见投放域总览映射表
