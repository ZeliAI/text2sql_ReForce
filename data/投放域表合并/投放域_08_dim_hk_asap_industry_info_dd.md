# dim_hk_asap_industry_info_dd
> 返回 [投放域总览](./投放域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.dim_hk_asap_industry_info_dd |
| 层级 | DIM（维度层） |
| 主键 | industry_org_id |
| 分区 | dt (yyyyMMdd) |
| 说明 | 行业信息维度表，存储行业组织架构和分类信息 |

---

## 二、核心字段列表
### 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| industry_org_id | string | 行业ID | INDUSTRY_ORG_001 | 高 |
| industry_org_name | string | 行业名称 | 数字生活_积分, 数字金融_自营金融, 数字支付_交通 | 高 |
| parent_industry_org_id | string | 父级行业ID | 用于构建行业层级 | 中 |
| industry_level | int | 行业层级 | 1, 2, 3 | 中 |
| industry_status | string | 行业状态 | ACTIVE, INACTIVE | 低 |
| gmt_create | string | 创建时间 | 2026-01-01 00:00:00 | 低 |
| gmt_modified | string | 修改时间 | 2026-03-20 15:30:00 | 低 |
| environment | string | 环境标识 | R: Released（线上）/ P: Pre（预发） | 低 |
| dt | string | 日期分区 | 20260322 | 高 |

---

## 三、行业分类示例
常见行业组织名称：

- 数字生活_积分
- 数字生活_本地优惠
- 数字生活_chill生活
- 数字金融_自营金融
- 数字金融_理财
- 数字支付_交通
- 数字支付_缴费
- 数娱_票务
- 数娱_游戏

---

## 四、常用查询场景
### 4.1 查询所有活跃行业
```sql
SELECT 
    industry_org_id,
    industry_org_name,
    industry_level
FROM dim_hk_asap_industry_info_dd
WHERE dt = '${bizdate}'
  AND industry_status = 'ACTIVE'
  AND environment = 'R'
ORDER BY industry_org_name
```

### 4.2 查询一级行业分类
```sql
SELECT 
    industry_org_id,
    industry_org_name
FROM dim_hk_asap_industry_info_dd
WHERE dt = '${bizdate}'
  AND industry_level = 1
  AND industry_status = 'ACTIVE'
  AND environment = 'R'
ORDER BY industry_org_name
```

### 4.3 查询某行业的子行业
```sql
SELECT 
    industry_org_id,
    industry_org_name,
    industry_level
FROM dim_hk_asap_industry_info_dd
WHERE dt = '${bizdate}'
  AND parent_industry_org_id = '${parent_industry_org_id}'
  AND industry_status = 'ACTIVE'
  AND environment = 'R'
ORDER BY industry_org_name
```

---

## 五、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **环境过滤**：线上数据查询时必须加 environment = 'R'
3. **状态说明**：ACTIVE-活跃, INACTIVE-非活跃
4. **关联使用**：通常与 DWS/DWD 表关联，按行业维度统计曝光、点击等指标
5. **层级关系**：通过 parent_industry_org_id 和 industry_level 构建行业树形结构
