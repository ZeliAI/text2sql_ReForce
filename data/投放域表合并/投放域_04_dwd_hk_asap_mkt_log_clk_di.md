# dwd_hk_asap_mkt_log_clk_di
> 返回 [投放域总览](./投放域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.dwd_hk_asap_mkt_log_clk_di |
| 层级 | DWD（明细层） |
| 主键 | - |
| 外键 | space_code, content_id → dws_hk_asap_mkt_distribute_index_1d |
| 分区 | dt (yyyyMMdd) |
| 说明 | 投放域点击日志日增明细表，用于按用户/事件追踪点击行为 |

> ⚠️ **选表说明**：本表为 DWD 明细层，包含每条点击事件记录。仅在需要用户级明细（如 experiment_ids、utdid、log_type 等）或需关联明细维度时才使用。一般点击统计请优先使用 DWS 表。

---

## 二、核心字段列表
### 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| loged_time | string | 上传服务器记录时间 | 2026-03-22 18:27:24.675 | 中 |
| log_time | string | 客户端日志时间 | 2026-03-22 18:27:24.675 | 高 |
| alipay_product_id | string | 产品ID | WALLET_HK_ANDROID,WALLET_HK_IOS | 高 |
| alipay_product_version | string | 产品版本 | 10.3.96, 9.8.0 | 中 |
| tcid | string | 设备id | 460000000000000\|nskvy9pm6ob500m | 高 |
| session_id | string | 会话id | 307B7E2F-AD1D-407B-AD48-8F6EB14B8D26 | 高 |
| user_id | string | 用户id(2088开头) | 2088222168756612 | 高 |
| behaviorid | string | 行为id(clicked) | clicked | 高 |
| spm | string | 当前点击的spm | a1.b2.c3.d4 | 高 |
| spm_a | string | 当前点击spm的a位 | a1 | 中 |
| spm_b | string | 当前点击spm的b位 | b2 | 中 |
| spm_c | string | 当前点击spm的c位 | c3 | 中 |
| spm_d | string | 当前点击spm的d位 | d4 | 中 |
| utdid | string | utdid | ZdKwcV9lBtsDAEQ5OubWwsdY | 高 |
| device_model | string | 设备号 | iPhone16 2 | 中 |
| os_version | string | 操作系统版本 | 17.6.1 | 中 |
| network | string | 网络 | LTE\|-- | 中 |
| language | string | 语言 | zh-CN, en | 低 |
| ip | string | ip | 192.168.1.1, 114.114... | 中 |
| ip_country | string | 从ip中解析出来的国家名称 | 中国, USA | 低 |
| ip_province | string | 从ip中解析出来的省份名称 | 浙江省, California | 低 |
| ip_city | string | 从ip中解析出来的城市名称 | 杭州市, San Francisco | 低 |
| log_type | string | 日志来源渠道 | native, h5, cashier | 中 |
| experiment_ids | string | ABTest的experimentIds | exp_12345_groupB | 高 |
| space_code | string | 展位code | 举例： HK_HOME_PAGE_FEEDS_LIST | 高 |
| space_name | string | 展位名称 | 举例： 首页feeds | 高 |
| delivery_task_id | string | 投放任务ID | 外键→dim_hk_asap_mkt_delivery_task_dd<br/>示例：DELIVERY_PUSH_TASK_20260322_001 | 高 |
| delivery_task_name | string | 投放任务名称 | 举例： 12.29-生活频道-北上-$90 | 高 |
| industry_org_id | string | 行业ID | 外键→dim_hk_asap_industry_info_dd | 中 |
| industry_org_name | string | 行业名称 | 数字生活_积分, 数字金融_自营金融等 | 中 |
| content_id | string | 投放内容ID | 举例：sgprodsg_maga_hktraffic_static_content... | 高 |
| title | string | 投放内容标题 | 举例：流失電訊用戶首頁卡片 | 高 |
| content_type | string | 投放内容类型 | STATIC_CONTENT, POINT_TASK, BENEFIT, SALE_BENEFIT, EXCHANGE, BRAND, TICKET, MINI_APP, SIM | 高 |
| traffic_type | string | 流量类型 | NON_COMMERCIAL_COMPETITIVE(竞争流量), COMMERCIAL(商业化流量), NON_COMMERCIAL_BUDGET(预算流量) | 高 |
| slot_id | int | 坑位ID | 1, 2, 3, 4, 5, 6, 7, 8 | 中 |
| is_public | tinyint | 是否公域展位 | 1（公域）/ 0（非公域） | 中 |
| delivery_task_status | string | 投放任务状态 | RELEASED | 低 |
| dt | string | 时间分区 | 20260327 | 高 |

---

## 三、日志来源说明
log_type 字段枚举值：

- native：来自uniform_behavior的文件采集
- h5：来自webapp文件的采集
- cashier：来自收银台日志的采集

---

## 四、常用查询场景
### 4.1 统计点击PV/UV
```sql
SELECT 
    dt,
    COUNT(*) AS clk_pv,
    COUNT(DISTINCT user_id) AS clk_uv
FROM dwd_hk_asap_mkt_log_clk_di
WHERE dt = '${bizdate}'
GROUP BY dt
```

### 4.2 按任务统计点击量
```sql
SELECT 
    delivery_task_id,
    COUNT(*) AS total_clk,
    COUNT(DISTINCT user_id) AS clk_uv
FROM dwd_hk_asap_mkt_log_clk_di
WHERE dt = '${bizdate}'
GROUP BY delivery_task_id
ORDER BY total_clk DESC
```

### 4.3 按渠道统计点击量
```sql
SELECT 
    log_type,
    COUNT(*) AS clk_pv,
    COUNT(DISTINCT user_id) AS clk_uv
FROM dwd_hk_asap_mkt_log_clk_di
WHERE dt = '${bizdate}'
GROUP BY log_type
```

### 4.4 计算CTR点击率（关联曝光表）
```sql
SELECT 
    t.delivery_task_id,
    SUM(t.expo_pv) AS expo_pv,
    SUM(t.clk_pv) AS clk_pv,
    ROUND(SUM(t.clk_pv) / NULLIF(SUM(t.expo_pv), 0), 4) AS ctr
FROM (
    SELECT 
        delivery_task_id,
        0 AS expo_pv,
        COUNT(*) AS clk_pv
    FROM dwd_hk_asap_mkt_log_clk_di
    WHERE dt = '${bizdate}'
    GROUP BY delivery_task_id
    
    UNION ALL
    
    SELECT 
        delivery_task_id,
        COUNT(*) AS expo_pv,
        0 AS clk_pv
    FROM dwd_hk_asap_mkt_log_expo_di
    WHERE dt = '${bizdate}'
    GROUP BY delivery_task_id
) t
GROUP BY t.delivery_task_id
```

---

## 五、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **DWD 定位**：本表为明细层，每条记录代表一次点击事件
3. **优先使用 DWS**：常规统计请优先使用 DWS 表，仅在需要明细维度（experiment_ids、utdid 等）时使用本表
4. **关联维度**：通过 delivery_task_id 关联投放任务维度表获取任务详情
