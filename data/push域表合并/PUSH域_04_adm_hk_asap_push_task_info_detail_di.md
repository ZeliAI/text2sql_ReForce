# adm_hk_asap_push_task_info_detail_di（push发送日志明细表）
> 返回 [push域 Schema 总览](./PUSH域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.adm_hk_asap_push_task_info_detail_di |
| 层级 | DWD（明细层） |
| 主键 | - (日志表无主键) |
| 外键 | delivery_push_task_id ,creative_id→ adm_hk_asap_dwd_push_task_info_dd |
| 分区 | dt (yyyyMMdd) |
| 说明 | push发送日志明细表，记录每个用户/设备的发送记录 |

---

## 二、核心字段列表
## 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| dt | string | 日期 | 格式: yyyyMMdd   示例：20260322 | �� 高 |
| delivery_push_task_id | string | push任务ID | 外键→adm_hk_asap_dwd_push_task_info_dd | 示例：PUSH_TASK_ID20260130100136809 |
| user_id | string | 用户ID | 示例：208810217... | �� 高 |
| service_code | string | service_code | 示例：GT_SC_alipayHK_push | ⚡ 中 |
| creative_id | string | 文案ID | 示例：STATIC_CONTENT20260401100483433 | ⚡ 中 |
| send_time | string | 发送时间 | 格式：yyyy-MM-dd HH:mm:ss  示例：2026-03-22 14:30:25 | �� 高 |
| send_status | string | 发送状态 | 枚举：SEND_SUCCESS, SEND_FAIL   示例：SEND_SUCCESS | �� 高 |
| send_fail_msg | string | 失败原因 | 示例：ALL_PUSH_TASK_TARGETING_FILTER_NOT_PASS | ⚡ 中 |
| push_title | string | 文案标题 | 示例：4月北上！ | ⚡ 中 |
| push_sub_title | string | 文案副标题 | 示例：券立即享$5优惠！ | ⚡ 中 |
| push_url | string | 文案URL | JSON格式 | 示例：alipayhk://platformapi/startApp?appId=85200023 |
| business_unit_code | string | 业务单元代码 | 示例：SG_MAGA_HK | ⚡ 中 |
| environment | string | 环境 | 枚举：R, P   示例：R | �� 高 |
| msg_id | string | msg_id | 示例：ASAP_8b1be6f34c98495f1658f31d6b8356fe | ⚡ 中 |
| extend_info | string | 扩展字段 | JSON格式 | 示例：{} |
| tnt_id | string | 租户id | 示例：ALIPW3HK | ❄️ 低 |

## 指标字段
| 字段名 | 类型 | 描述 | 使用方式 | 热度 |
| --- | --- | --- | --- | --- |
| send_count | bigint | 发送次数 | 预存字段，直接 COUNT(calculated) | �� 高 |
| send_success_count | bigint | 发送成功次数 | WHERE send_status = 'SEND_SUCCESS' COUNT | �� 高 |
| send_fail_count | bigint | 发送失败次数 | WHERE send_status = 'SEND_FAIL' COUNT | ⚡ 中 |

---

## 三、发送状态说明
send_status 字段枚举值：

- SEND_SUCCESS：发送成功
- SEND_FAIL：发送失败

常见失败原因（send_fail_msg）：

- ALL_PUSH_TASK_TARGETING_FILTER_NOT_PASS：任务定向过滤未通过

---

## 四、常用查询场景
### 4.1 查询当天push发送统计
```sql
SELECT 
    delivery_push_task_id,
    send_status,
    COUNT(*) as send_cnt,
    COUNT(DISTINCT user_id) as send_uv
FROM adm_hk_asap_push_task_info_detail_di
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY delivery_push_task_id, send_status;
```

### 4.2 查询某用户当天的发送记录
```sql
SELECT 
    delivery_push_task_id,
    send_time,
    send_status,
    push_title,
    push_sub_title
FROM adm_hk_asap_push_task_info_detail_di
WHERE dt = '${bizdate}'
  AND user_id = '${user_id}'
  AND environment = 'R'
ORDER BY send_time DESC;
```

### 4.3 按发送状态统计
```sql
SELECT 
    send_status,
    COUNT(*) as cnt,
    COUNT(DISTINCT delivery_push_task_id) as task_cnt
FROM adm_hk_asap_push_task_info_detail_di
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY send_status;
```

### 4.4 按任务统计发送成功率
```sql
SELECT 
    delivery_push_task_id,
    COUNT(*) as total_send,
    SUM(CASE WHEN send_status = 'SEND_SUCCESS' THEN 1 ELSE 0 END) as success_count,
    ROUND(SUM(CASE WHEN send_status = 'SEND_SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM adm_hk_asap_push_task_info_detail_di
WHERE dt = '${bizdate}'
  AND environment = 'R'
GROUP BY delivery_push_task_id;
```

---

## 五、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **环境过滤**：查询时需要加上 `environment = 'R'` 只查询生产环境数据
3. **关联维度**：通过 delivery_push_task_id 关联 push 任务核心宽表 `adm_hk_asap_dwd_push_task_info_dd` 获取任务详情
4. **数据来源**：数据来自 push 发送系统和日志系统
5. **发送状态**：send_status 字段区分成功和失败记录，失败原因在 send_fail_msg 字段中说明
