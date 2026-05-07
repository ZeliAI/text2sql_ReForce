# dim_hk_asap_mkt_delivery_task_dd
> 返回 [投放域总览](./投放域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.dim_hk_asap_mkt_delivery_task_dd |
| 层级 | DIM（维度层） |
| 主键 | delivery_task_id |
| 外键 | space_id → dim_hk_asap_space_info_dd |
| 外键 | industry_org_id → dim_hk_asap_industry_info_dd |
| 分区 | dt (yyyyMMdd) |
| 说明 | 投放任务维度表，存储投放任务的配置信息和状态 |

---

## 二、核心字段列表
### 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| delivery_task_id | string | 投放任务ID | DELIVERY_TASK_20260322_001 | 高 |
| delivery_task_name | string | 投放任务名称 | 12.29-生活频道-北上-$90 | 高 |
| delivery_task_status | string | 投放任务状态 | RELEASED, PAUSED, FINISHED | 高 |
| space_id | string | 展位ID | 外键→dim_hk_asap_space_info_dd | 高 |
| space_code | string | 展位CODE | HK_HOME_PAGE_FEEDS_LIST | 高 |
| space_name | string | 展位名称 | 首页feeds | 高 |
| industry_org_id | string | 行业ID | 外键→dim_hk_asap_industry_info_dd | 高 |
| industry_org_name | string | 行业名称 | 数字生活_积分, 数字金融_自营金融 | 高 |
| traffic_type | string | 流量类型 | NON_COMMERCIAL_COMPETITIVE, COMMERCIAL, NON_COMMERCIAL_BUDGET | 高 |
| is_public | tinyint | 是否公域展位 | 1（公域）/ 0（非公域） | 中 |
| start_time | string | 投放开始时间 | 2026-03-22 00:00:00 | 高 |
| end_time | string | 投放结束时间 | 2026-04-22 23:59:59 | 高 |
| gmt_create | string | 创建时间 | 2026-03-20 10:00:00 | 中 |
| gmt_modified | string | 修改时间 | 2026-03-21 15:30:00 | 中 |
| environment | string | 环境标识 | R: Released（线上）/ P: Pre（预发） | 低 |
| dt | string | 日期分区 | 20260322 | 高 |

---

## 三、常用查询场景
### 3.1 查询进行中的投放任务
```sql
SELECT 
    delivery_task_id,
    delivery_task_name,
    space_name,
    industry_org_name,
    start_time,
    end_time
FROM dim_hk_asap_mkt_delivery_task_dd
WHERE dt = '${bizdate}'
  AND delivery_task_status = 'RELEASED'
  AND start_time <= NOW()
  AND end_time >= NOW()
  AND environment = 'R'
ORDER BY start_time DESC
```

### 3.2 按行业统计任务数量
```sql
SELECT 
    industry_org_name,
    COUNT(*) AS task_cnt
FROM dim_hk_asap_mkt_delivery_task_dd
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY industry_org_name
ORDER BY task_cnt DESC
```

### 3.3 查询某展位的任务列表
```sql
SELECT 
    delivery_task_id,
    delivery_task_name,
    delivery_task_status,
    traffic_type,
    start_time,
    end_time
FROM dim_hk_asap_mkt_delivery_task_dd
WHERE dt = '${bizdate}'
  AND space_name = '首页feeds'
  AND environment = 'R'
ORDER BY gmt_create DESC
```

---

## 四、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **环境过滤**：线上数据查询时必须加 environment = 'R'
3. **状态说明**：RELEASED-已发布, PAUSED-已暂停, FINISHED-已完成
4. **关联使用**：通常与 DWS/DWD 表关联，获取任务的展位和行业信息
