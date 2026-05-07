# adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di（push慢表）
> 返回 [push域 Schema 总览](./PUSH域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di |
| 层级 | DWS（明细层） |
| 主键 | - (日志表无主键) |
| 外键 | delivery_push_task_id,creative_id → adm_hk_asap_dwd_push_task_info_dd |
| 分区 | dt (yyyyMMdd) |
| 说明 | push慢表，用于分析push消息的发送曝光及点击转化效果，聚焦慢查询场景 |

---

## 二、核心字段列表
### 维度字段
| 编号 | 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- | --- |
| 1 | delivery_push_task_id | STRING | push任务ID | PUSH_TASK_ID20260414100211431 | �� 高 |
| 2 | delivery_push_task_name | STRING | push任务名称 | 202604-生活頻道-本地優惠大牌餐飲券-Push | ⚡ 中 |
| 3 | industry_org_id | STRING | 行业组织ID | INDUSTRY_ORG_09_CHILL_LIFE_02 | ⚡ 中 |
| 4 | industry_org_name | STRING | 行业组织名称 | 数字生活_chill生活 | ⚡ 中 |
| 6 | creative_id | STRING | 文案ID | STATIC_CONTENT20260415100532789 | �� 高 |
| 7 | creative_type | STRING | 文案类型 | Manual, LLM | ⚡ 中 |
| 8 | creative_tag | STRING | 文案标签 | 精明攻略型 | ⚡ 中 |
| 11 | send_time | STRING | 发送时间-时间戳 | 1776582012260 | �� 高 |
| 12 | send_date | STRING | 发送时间-东八区 | 20260419 | �� 高 |
| 13 | user_id | STRING | 用户ID | 2160210000005829 | �� 高 |
| 14 | send_status | STRING | push任务发送状态 | SEND_SUCCESS /SEND_FAIL | ⚡ 中 |
| 15 | send_fail_msg | STRING | push任务失败原因 | ALL_PUSH_TASK_TARGETING_FILTER_NOT_PASS | ❄️ 低 |
| 16 | push_title | STRING | push标题 | ��️享受美食前先買張券，即慳超多！即買�� | ⚡ 中 |
| 17 | push_sub_title | STRING | push副标题 | alipayhk://platformapi/startApp?appId=2060090000320265 | ⚡ 中 |
| 18 | push_url | STRING | push URL | alipayhk://platformapi/startApp | ⚡ 中 |
| 22 | model | STRING | 机型，ANDROID/IOS | IOS, ANDROID | �� 高 |
| 23 | user_lifecycle | STRING | 用户生命周期 | 新手期用户,成长期用户,成熟期用户,衰退期用户,流失期用户,沉默期用户 | ⚡ 中 |
| 24 | user_value | STRING | 用户价值 | 高价值用户,一般价值用户,重点发展用户,一般发展用户,重点保持用户,一般保持用户,重点挽留用户,低价值用户 | ⚡ 中 |
| 25 | user_activity_level | STRING | 用户活跃分层 | 高频,中频,低频,流失,沉默 | �� 高 |
| 26 | push_type | STRING | push类型 | 营销Push，平台Push，战略Push，商业化Push,事件push | ⚡ 中 |
| 29 | push_task_start_date | STRING | push任务开始时间 | 2026-04-15 16:00:00.000000 | �� 高 |
| 30 | push_task_end_date | STRING | push任务结束时间 | 2026-04-30 15:59:59.000000 | �� 高 |
| 36 | push_task_gmt_create | STRING | push任务创建时间 | 2026-04-14 09:26:16.105000 | �� 高 |
| 48 | is_expo | BIGINT | 是否曝光，1是0否 | 0, 1 | �� 高 |
| 49 | expo_pv | BIGINT | 曝光次数 | 1，2，3 | ❄️ 低 |
| 54 | is_clk | BIGINT | 是否点击，1是0否 | 0, 1 | �� 高 |
| 55 | clk_pv | BIGINT | 点击次数 | 1，2，3 | ❄️ 低 |
| 57 | dt | STRING | 日期分区 | 20260419 | �� 高 |

### 度量字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| is_expo | BIGINT | 是否曝光 | 1/0 | �� 高 |
| expo_pv | BIGINT | 曝光次数 | 1，3，4 | ❄️ 低 |
| is_clk | BIGINT | 是否点击 | 1/0 | �� 高 |
| clk_pv | BIGINT | 点击次数 | 1，2，3 | ❄️ 低 |

---

## 三、常用查询场景
### 3.1 按任务统计整体效果
```sql
SELECT 
    delivery_push_task_id,
    count(1) as send_pv,
    COUNT(if(is_expo='1',1,null)) AS total_expo_pv,
    COUNT(if(is_clk='1',1,null)) AS total_clk_pv,
    COUNT(DISTINCT user_id) AS user_cnt
FROM adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di
WHERE dt = '${bizdate}'
GROUP BY delivery_push_task_id
ORDER BY total_expo DESC
```

### 3.2 计算整体CTR转化率
```sql
SELECT  delivery_push_task_id
        ,COUNT(IF(is_expo = '1', 1, NULL)) AS total_expo_pv
        ,COUNT(IF(is_clk = '1', 1, NULL)) AS total_clk_pv
        ,ROUND(COUNT(IF(is_clk = '1', 1, NULL)) / NULLIF(COUNT(IF(is_expo = '1', 1, NULL)), 0), 4) AS ctr
FROM    anthk_sg.adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di
WHERE   dt = '${bizdate}'
GROUP BY delivery_push_task_id 
```

### 3.3 按用户分层分析
```sql
SELECT 
    user_lifecycle,
    user_value,
    user_activity_level,
    COUNT(DISTINCT user_id) AS user_cnt,
    SUM(is_expo) AS expo_cnt,
    SUM(is_clk) AS clk_cnt,
    ROUND(SUM(is_clk) / NULLIF(SUM(is_expo), 0), 4) AS ctr
FROM adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di
WHERE dt = '${bizdate}'
GROUP BY user_lifecycle, user_value, user_activity_level
```

### 3.4 按渠道分析
```sql
SELECT 
    environment,
    push_channel_type,
    COUNT(DISTINCT delivery_push_task_id) AS task_cnt,
    SUM(is_expo) AS expo_cnt,
    SUM(is_clk) AS clk_cnt,
    ROUND(SUM(is_clk) / NULLIF(SUM(is_expo), 0), 4) AS ctr
FROM adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di
WHERE dt = '${bizdate}'
GROUP BY environment, push_channel_type
```

---

## 四、注意事项
1. **分区字段**：dt (yyyyMMdd) 为分区字段，查询时必须指定
2. **点击定义**：点击定义为用户点击push消息后产生有效跳转行为，且is_clk=1
3. **曝光定义**：曝光定义为push消息到达设备并被展示，且is_expo=1
4. **关联维度**：通过 delivery_push_task_id 关联 push 任务核心宽表 `adm_hk_asap_dwd_push_task_info_dd` 获取任务详情
5. **数据来源**：数据来自埋点系统上报的曝光和点击事件日志
6. **慢表定位**：本表专门用于分析push消息处理性能问题，通过暴露时间差来识别慢任务
