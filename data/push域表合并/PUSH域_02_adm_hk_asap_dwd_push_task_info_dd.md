# adm_hk_asap_dwd_push_task_info_dd（push任务核心宽表）
> 返回 [push域 Schema 总览](./PUSH域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.adm_hk_asap_dwd_push_task_info_dd |
| 层级 | DWD（明细层） |
| 主键 | delivery_push_task_id, creative_id |
| 外键 | delivery_push_task_id → push任务 |
| 外键 | creative_id → antsg_nods.ods_imcdp_static_content |
| 外键 | industry_org_id → antsg_nods.ods_imcdp_biz_line_org |
| 分区 | dt (yyyyMMdd) |
| 说明 | push任务核心宽表，汇总所有任务、文案、业务线、AIGC文案等所有信息 |

---

## 二、字段列表
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| dt | string | 日期 | 格式: yyyyMMdd   示例：20260322 | 高 |
| delivery_push_task_id | string | push任务ID | 主键   示例：DELIVERY_PUSH_TASK_20260322_001 | 高 |
| creative_id | string | 文案ID | 外键→antsg_nods.ods_imcdp_static_content   示例：CRM_001 | 高 |
| industry_org_id | string | 行业组织ID | 外键→antsg_nods.ods_imcdp_biz_line_org   示例：IO_001 | 高 |
| push_type | string | push类型 | 枚举：PUSH_MARKETING, PUSH_PLATFORM, PUSH_STRATEGY, PUSH_COMMERCIAL, PUSH_EVENT | 高 |
| creative_type | string | 文案类型 | 枚举：Manual, LLM   示例：LLM | 高 |
| status | string | 任务状态 | 枚举：INIT, RUNNING, PAUSE, FINISH   示例：RUNNING | 高 |
| user_id | string | 用户ID | 示例：208810217... | 中 |
| push_channel_type | string | push渠道类型 | 示例：ALIAPP | 中 |
| environment | string | 环境 | 枚举：R, P   示例：R | 高 |
| business_unit_code | string | 业务单元编码 | 示例：SG_MAGA_HK | 高 |
| biz_line_name_lv1 | string | 一级业务线名称 | 示例：钱包 | 高 |
| biz_line_name_lv2 | string | 二级业务线名称 | 示例：运营 | 中 |
| biz_line_name_lv3 | string | 三级业务线名称 | 示例：营销 | 中 |
| industry_org_name | string | 行业组织名称 | 示例：综测 | 中 |
| gmt_create | datetime | 创建时间 | 示例：2026-03-22 14:30:25 | 中 |
| gmt_modified | datetime | 修改时间 | 示例：2026-03-22 15:00:00 | 中 |
| call_login | string | 负责工号 | 文案负责人工号   示例：zhangsan | 低 |
| aigc_text | string | AIGC生成文案 | 大模型生成的push文案内容   示例：您的钱包余额不足... | 中 |

---

## 三、常用查询场景
### 3.1 查询当天运行中的任务
```sql
SELECT 
    delivery_push_task_id,
    push_type,
    creative_type,
    biz_line_name_lv1,
    industry_org_name,
    gmt_create
FROM adm_hk_asap_dwd_push_task_info_dd
WHERE dt = '${bizdate}'
  AND status = 'RUNNING'
  AND environment = 'R'
  AND business_unit_code = 'SG_MAGA_HK';
```

### 3.2 按业务线统计任务数
```sql
SELECT 
    biz_line_name_lv1,
    COUNT(DISTINCT delivery_push_task_id) as task_cnt,
    COUNT(DISTINCT CASE WHEN creative_type = 'AIGC' THEN delivery_push_task_id END) as aigc_task_cnt
FROM adm_hk_asap_dwd_push_task_info_dd
WHERE dt = '${bizdate}'
  AND environment = 'R'
  AND business_unit_code = 'SG_MAGA_HK'
GROUP BY biz_line_name_lv1;
```

### 3.3 按文案类型统计
```sql
SELECT 
    creative_type,
    COUNT(DISTINCT delivery_push_task_id) as task_cnt
FROM adm_hk_asap_dwd_push_task_info_dd
WHERE dt = '${bizdate}'
  AND environment = 'R'
  AND business_unit_code = 'SG_MAGA_HK'
GROUP BY creative_type;
```

### 3.4 按行业组织统计任务分布
```sql
SELECT 
    industry_org_name,
    COUNT(DISTINCT delivery_push_task_id) as task_cnt
FROM adm_hk_asap_dwd_push_task_info_dd
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY industry_org_name;
```

---

## 四、注意事项
1. **分区字段**：dt 为分区字段，查询时必须指定
2. **环境过滤**：查询时需要加上 `environment = 'R'` 只查询生产环境数据
3. **状态枚举**：status 字段枚举值说明
    - INIT：初始
    - RUNNING：运行中
    - PAUSED：已暂停
    - FINISH：已完成
4. **业务线多级结构**：支持一级、二级、三级业务线维度分析
5. **AIGC文案**：aigc_text 字段存储大模型生成的push文案内容
6. **关联维度**：通过 delivery_push_task_id 关联其他 push 相关表
