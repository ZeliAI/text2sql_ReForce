# dim_hk_asap_content_dd
> 返回 [投放域总览](./投放域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.dim_hk_asap_content_dd |
| 层级 | DIM（维度层） |
| 主键 | content_id |
| 分区 | dt (yyyyMMdd) |
| 说明 | 内容维度表，存储投放内容的配置信息和属性 |

---

## 二、核心字段列表
### 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| content_id | string | 投放内容ID | sgprodsg_maga_hktraffic_static_content... | 高 |
| title | string | 投放内容标题 | 流失電訊用戶首頁卡片 | 高 |
| content_type | string | 内容类型 | STATIC_CONTENT, POINT_TASK, BENEFIT, SALE_BENEFIT, EXCHANGE, BRAND, TICKET, MINI_APP, SIM | 高 |
| content_status | string | 内容状态 | ONLINE, OFFLINE | 高 |
| content_url | string | 内容链接 | https://example.com/campaign | 中 |
| gmt_create | string | 创建时间 | 2026-03-20 10:00:00 | 中 |
| gmt_modified | string | 修改时间 | 2026-03-21 15:30:00 | 中 |
| environment | string | 环境标识 | R: Released（线上）/ P: Pre（预发） | 低 |
| dt | string | 日期分区 | 20260322 | 高 |

---

## 三、内容类型说明
content_type 字段枚举值：

- STATIC_CONTENT：静态内容
- POINT_TASK：积分任务
- BENEFIT：权益
- SALE_BENEFIT：营销权益
- EXCHANGE：兑换
- BRAND：品牌
- TICKET：票务
- MINI_APP：小程序
- SIM：SIM卡

---

## 四、常用查询场景
### 4.1 查询在线内容列表
```sql
SELECT 
    content_id,
    title,
    content_type,
    gmt_create
FROM dim_hk_asap_content_dd
WHERE dt = '${bizdate}'
  AND content_status = 'ONLINE'
  AND environment = 'R'
ORDER BY gmt_create DESC
```

### 4.2 按内容类型统计数量
```sql
SELECT 
    content_type,
    COUNT(*) AS content_cnt
FROM dim_hk_asap_content_dd
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY content_type
ORDER BY content_cnt DESC
```

### 4.3 查询某类型的内容详情
```sql
SELECT 
    content_id,
    title,
    content_url,
    gmt_create
FROM dim_hk_asap_content_dd
WHERE dt = '${bizdate}'
  AND content_type = 'BENEFIT'
  AND content_status = 'ONLINE'
  AND environment = 'R'
ORDER BY gmt_create DESC
LIMIT 10
```

---

## 五、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **环境过滤**：线上数据查询时必须加 environment = 'R'
3. **状态说明**：ONLINE-在线, OFFLINE-下线
4. **关联使用**：通常与 DWS/DWD 表关联，获取内容的类型和状态信息
