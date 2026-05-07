# dim_hk_asap_space_info_dd
> 返回 [投放域总览](./投放域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.dim_hk_asap_space_info_dd |
| 层级 | DIM（维度层） |
| 主键 | space_id |
| 外键 | industry_org_id → dim_hk_asap_industry_info_dd |
| 分区 | dt (yyyyMMdd) |
| 说明 | 展位信息维度表，存储展位的配置信息和属性 |

---

## 二、核心字段列表
### 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| space_id | string | 展位ID | SPACE_001 | 高 |
| space_code | string | 展位CODE | HK_HOME_PAGE_FEEDS_LIST | 高 |
| space_name | string | 展位名称 | 首页feeds, 首页Banner样式A展位 | 高 |
| space_status | string | 展位状态 | ONLINE, OFFLINE | 高 |
| industry_org_id | string | 行业ID | 外键→dim_hk_asap_industry_info_dd | 高 |
| industry_org_name | string | 行业名称 | 数字生活_积分, 数字金融_自营金融 | 高 |
| is_public | tinyint | 是否公域展位 | 1（公域）/ 0（非公域） | 中 |
| space_type | string | 展位类型 | BANNER, FEEDS, CORNER, CARD | 中 |
| gmt_create | string | 创建时间 | 2026-01-15 10:00:00 | 低 |
| gmt_modified | string | 修改时间 | 2026-03-20 15:30:00 | 低 |
| environment | string | 环境标识 | R: Released（线上）/ P: Pre（预发） | 低 |
| dt | string | 日期分区 | 20260322 | 高 |

---

## 三、常用查询场景
### 3.1 查询所有在线展位
```sql
SELECT 
    space_id,
    space_code,
    space_name,
    industry_org_name,
    is_public
FROM dim_hk_asap_space_info_dd
WHERE dt = '${bizdate}'
  AND space_status = 'ONLINE'
  AND environment = 'R'
ORDER BY space_name
```

### 3.2 按行业统计展位数
```sql
SELECT 
    industry_org_name,
    COUNT(*) AS space_cnt
FROM dim_hk_asap_space_info_dd
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY industry_org_name
ORDER BY space_cnt DESC
```

### 3.3 查询公域展位列表
```sql
SELECT 
    space_id,
    space_code,
    space_name,
    industry_org_name
FROM dim_hk_asap_space_info_dd
WHERE dt = '${bizdate}'
  AND is_public = 1
  AND space_status = 'ONLINE'
  AND environment = 'R'
ORDER BY industry_org_name, space_name
```

---

## 四、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **环境过滤**：线上数据查询时必须加 environment = 'R'
3. **状态说明**：ONLINE-在线, OFFLINE-下线
4. **关联使用**：通常与 DWS/DWD 表关联，获取展位的行业和公域属性信息
5. **口语映射**：用户口语描述（如"腰封"、"支付结果页"）需转换为实际 space_name，详见投放域总览映射表
