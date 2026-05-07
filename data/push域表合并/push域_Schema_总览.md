# push域 Schema 总览

本文档为push域Schema元数据总览，包含域说明、表索引、选表规则、**指标口径**、业务术语映射、通用取数样例。各表字段详情见关联文档。

**原则：SKILL.md只记录域注册信息，完整Schema从本语雀文档按需拉取。**  
拉取方式：`yuque-mcp skylark_user_doc_detail`，命名空间 `gaespg/tkz7r8`，slug `uqedqi6gs4qycgt9`

---

## 一、域说明
push域覆盖营销push业务，包含Push消息发送、曝光追踪、点击效果等核心场景。

**业务范围：**

- Push发送效果：发送量、到达量、曝光量、点击量等指标分析
- Push任务管理：任务创建、生效时间、状态流转等
- Push文案管理：人工文案、AIGC文案、创意标签等
- Push渠道区分：机型、环境、业务线等维度分析

---

## 二、核心概念
| **概念** | **英文** | **说明** | **关联表** |
| --- | --- | --- | --- |
| Push任务 | Push Task | push任务，控制投放时间、范围、内容等 | **adm_hk_asap_dwd_push_task_info_dd** (核心DWD宽表，汇总所有任务、文案、业务线、行业组织、AIGC文案等所有信息) |
| Push文案 | Creative | push文案，包含标题、副标题、URL等 | antsg_nods.ods_imcdp_static_content |
| Push发送 | Push Send | 消息发送到设备 | anthk_sg.dwd_intl_gloc_hk_push_out_history_750_dd |
| Push曝光 | Push Exposure | 消息在设备上展示 | anthk_sg.dwd_evt_hk_app_log_exposure_di |
| Push点击 | Push Click | 用户点击push消息 | anthk_sg.dwd_evt_hk_app_log_clk_di |
| 业务线 | Business Line | 业务分类维度，用于组织投放资源 | antsg_nods.ods_imcdp_biz_line_org |
| AIGC文案 | AIGC Creative | 大模型生成的push文案 | ods_imcdp_static_content.extend_info.llmPushTextParam |


**重要说明**：push任务、push文案、业务线等信息都汇总在同一个核心DWD宽表 **adm_hk_asap_dwd_push_task_info_dd** 中。业务线是核心的组织分类维度，包含多级结构（一级、二级、三级）以及行业组织信息。

---

## 三、表层级关系
```plain
┌──────────────────────────────────────────────────┐
│               ADS 应用层                             │
│  adm_hk_asap_push_task_info_fast_ds              │  (快表：T+5分钟延迟)
│  adm_hk_asap_push_task_info_slow_ds              │  (慢表：T+2小时延迟)
│  adm_hk_asap_push_close_ds                      │  (关闭任务)
│  adm_asap_push_aigc_task_running_dd             │  (AIGC任务running全量，属DWD层)
│  adm_asap_push_aigc_trfc_analysis_di           │  (AIGC流量分析)
│  （按天分析，发送/曝光/点击等指标）                │
└──────────────────────────────────────────────────┘
                          ▲（聚合自）
┌──────────────────────────────────────────────────┐
│               DWS 汇总层                           │
│  adm_hk_asap_dwd_push_send_expo_clk_detail_fast_di  │  (T+5min，用户级汇总)
│  adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di  │  (T+2hr，用户级汇总)
│  （按天汇总每个用户每个任务的曝光和点击指标）          │
└──────────────────────────────────────────────────┘
                          ▲（聚合自）
┌──────────────────────────────────────────────────┐
│               DWD 明细层                           │
│  adm_hk_asap_dwd_push_task_info_dd               │  核心宽表
│  adm_hk_asap_push_task_info_detail_di            │  发送日志明细
│  adm_hk_asap_dwd_push_log_expo_di              │  曝光日志明细（小时分区）
│  adm_hk_asap_dwd_push_log_clk_di               │  点击日志明细（小时分区）
└──────────────────────────────────────────────────┘
                          ▲（关联）
┌──────────────────────────────────────────────────┐
│              ODS/I 源表层                         │
│  antsg_nods.ods_imcdp_delivery_push_task         │ push任务表
│  antsg_nods.ods_imcdp_static_content            │ push文案静态内容表
│  antsg_nods.ods_imcdp_biz_line_org            │ 业务线配置表
│  anthk_sg.dwd_intl_gloc_hk_push_out_history_750_dd    │ push发送历史表
│  anthk_sg.dwd_evt_hk_app_log_exposure_di       │ app曝光日志表
│  anthk_sg.dwd_evt_hk_app_log_clk_di           │ app点击日志表
└──────────────────────────────────────────────────┘
```

---

## 四、表索引
| 表名 | 层级 | 主键 | 核心外键 | 说明 | 详情文档 |
| --- | --- | --- | --- | --- | --- |
| **adm_hk_asap_dwd_push_task_info_dd** | DWD | delivery_push_task_id, creative_id | delivery_push_task_id, creative_id | **push任务明细宽表（核心表）** - 汇总push任务、文案、业务线、行业组织、AIGC文案等所有信息 | [查看](https://yuque.antfin.com/gaespg/tkz7r8/dfdtuqh5yhnqb1ko) |
| adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di | DWS | - | delivery_push_task_id, creative_id，user_id | 香港用户-ASAP-push消息-push发送-曝光-点击明细表-慢表 | [查看](https://yuque.antfin.com/gaespg/tkz7r8/gvduxdytx6etx82q) |
| adm_asap_push_aigc_task_running_dd | DWD | delivery_push_task_id, creative_id | delivery_push_task_id | AIGC任务running全量表 | [查看](https://yuque.antfin.com/gaespg/tkz7r8/ng9h4png7aa4l35i) |
| adm_hk_asap_push_task_info_detail_di | DWD | - | delivery_push_task_id | push发送日志明细表 | [查看](https://yuque.antfin.com/gaespg/tkz7r8/hhe0mz2dfyu3ufrm) |
| adm_hk_asap_dwd_push_log_expo_di | DWD | - | delivery_push_task_id | push曝光日志明细表（小时分区） | [查看](https://yuque.antfin.com/gaespg/tkz7r8/aytz5keagrx1pzc5) |
| adm_hk_asap_dwd_push_log_clk_di | DWD | - | delivery_push_task_id | push点击日志明细表（小时分区） | [查看](https://yuque.antfin.com/gaespg/tkz7r8/sxszhqd3hp7q9s1t) |


---

## 五、选表规则（NL2SQL核心）
**核心原则：DWS优先，明细字段才降级DWD。**

| 场景 | 使用表 | 理由 |
| --- | --- | --- |
| 查发送量/曝光量/点击量/CTR等聚合指标（任务维度） | **ADS** adm_hk_asap_push_task_info_fast/slow_ds | 已按天汇总，性能最优 |
| 查push任务详情/文案信息/任务状态/业务线 | **DWD** adm_hk_asap_dwd_push_task_info_dd | 核心宽表，包含所有维度信息；业务线作为关键的组织维度，包含一级、二级、三级等多级结构 |
| 需要用户级（单个用户）的发送/曝光/点击明细 | **DWS** adm_hk_asap_dwd_push_send_expo_clk_detail_fast/slow_di | 汇总层有用户级数据 |
| AIGC任务分析（running状态/任务类型） | **DWD** adm_asap_push_aigc_task_running_dd | 专用AIGC任务表 |
| AIGC流量分析（累计指标/创意效果对比） | **ADS** adm_asap_push_aigc_trfc_analysis_di | 专用AIGC流量表 |
| 曝光/点击日志明细分析 | **DWD** adm_hk_asap_dwd_push_log_expo_di / log_clk_di | 明细层日志表 |


```plain
判断流程（任务维度）：
用户需求 
  → 需要任务详情/文案信息/业务线？
       是 → 使用 DWD (adm_hk_asap_dwd_push_task_info_dd)
       否 → AIGC分析？
             是 → 使用 ADS (adm_asap_push_aigc_trfc_analysis_di)
             否 → 指标聚合？
                   是 → 需要用户级明细？
                         是 → 使用 DWS (adm_hk_asap_dwd_push_send_expo_clk_detail_fast/slow_di)
                         否 → 使用 ADS (adm_hk_asap_push_task_info_fast/slow_ds)
```

---

## 六、指标口径（NL2SQL核心）
### 6.1 ADS口径（优先使用）
> 基于 `adm_hk_asap_push_task_info_fast/slow_ds`，查询时必须加 `AND environment = 'R'`  
快表：T+5分钟延迟  
慢表：T+2小时延迟
>

| 指标名称 | ADS计算公式 | 说明 |
| --- | --- | --- |
| 发送量PV | SUM(send_cnt_pv) | push消息发送总数 |
| 发送成功量PV | SUM(send_success_cnt_pv) | push成功发送到设备数 |
| 曝光量PV | SUM(exposure_pv) | push消息在设备上的展示次数 |
| 点击量PV | SUM(click_pv) | 用户点击push消息次数 |
| 发送量UV | SUM(send_cnt_uv) | 发送给不同用户的数量 |
| 曝光量UV | SUM(exposure_uv) | 不同用户看到push消息的数量 |
| 点击量UV | SUM(click_uv) | 不同用户点击push消息的数量 |
| PV CTR | SUM(click_pv) / NULLIF(SUM(exposure_pv), 0) | 点击PV / 曝光PV，保留4位小数 |
| UV CTR | SUM(click_uv) / NULLIF(SUM(exposure_uv), 0) | 点击UV / 曝光UV，保留4位小数 |


### 6.2 DWD口径（降级使用，任务维度）
> 基于 `adm_hk_asap_dwd_push_task_info_dd`（核心宽表）
>

| 指标名称 | DWD计算公式 | 说明 |
| --- | --- | --- |
| 总任务数 | COUNT(DISTINCT delivery_push_task_id) | push任务总数 |
| 运行中任务数 | COUNT(DISTINCT CASE WHEN status = 'RUNNING' THEN delivery_push_task_id END) | 当前运行中的任务数 |
| 按业务线统计 | COUNT(DISTINCT CASE WHEN biz_line_code_lv1 = 'xxx' THEN delivery_push_task_id END) | 按一级业务线统计任务数 |


### 6.3 DWS口径（用户级汇总）
> 基于 `adm_hk_asap_dwd_push_send_expo_clk_detail_fast/slow_di`
>

| 指标名称 | DWS计算公式 | 说明 |
| --- | --- | --- |
| 用户级曝光计数 | SUM(expo_count) | 某用户某任务的曝光次数 |
| 用户级点击计数 | SUM(clk_count) | 某用户某任务的点击次数 |
| 用户级CTR | SUM(clk_count) / NULLIF(SUM(expo_count), 0) | 用户级点击率 |


---

## 七、业务术语映射（NL2SQL核心）
### 7.1 push类型
| **用户说的** | **push_type实际值** |
| --- | --- |
| 营销Push | PUSH_MARKETING |
| 平台Push | PUSH_PLATFORM |
| 策略Push | PUSH_STRATEGY |
| 商业化Push | PUSH_COMMERCIAL |
| 事件Push | PUSH_EVENT |


### 7.2 文案类型
| **用户说的** | **creative_type实际值** |
| --- | --- |
| 人工文案 | MANUAL / 空 |
| AIGC文案 | LLM / AIGC |
| 大模型文案 | LLM / AIGC |
| 规则引擎 | RULE |
| 标签引擎 | LABEL |


### 7.3 文案标签
| **用户说的** | **creative_tag实际值** |
| --- | --- |
| 利益导向 | Benefit_Oriented |
| 情感导向 | Emotion_Oriented |
| 紧急导向 | Urgency_Oriented |


### 7.4 任务状态
| **用户说的** | **status实际值** |
| --- | --- |
| 任务初始 | INIT |
| 任务运行中/生效中 | RUNNING |
| 任务暂停 | PAUSE |
| 任务完成 | FINISH |


### 7.5 push触发类型
| **用户说的** | **push_trigger_type实际值** |
| --- | --- |
| 自动触发 | auto |
| 人工触发 | manual |
| 算法触发 | alg |


### 7.6 业务线层级
业务线是push域的核心组织维度，包含多级结构：

| **层级** | **字段** | **说明** | 层级范围 |
| --- | --- | --- | --- |
| 一级业务线 | biz_line_name_lv1 / biz_line_code_lv1 | 业务线的最高层级，比如：钱包、支付 | 统计任务、报表的主要分类维度 |
| 二级业务线 | biz_line_name_lv2 / biz_line_code_lv2 | 业务线的二级分类，比如：运营、营销等 | 更细粒度的业务分类 |
| 三级业务线 | biz_line_name_lv3 / biz_line_code_lv3 | 业务线的最细粒度分类，比如：营销高端、营销低端等 | 用于精细化的业务运营分析 |
| 行业组织 | industry_org_name / industry_org_id | 行业组织是基于业务线、产品、渠道等维度的综合组织单位，比如：银行业务体系、保险业务体系 | 用于跨业务线的组织管理和资源分配 |


**数据来源**：业务线表 `antsg_nods.ods_imcdp_biz_line_org`  
**设计考虑**：

- 一级业务线是必填字段，每个push任务必须归属到一级业务线
- 二级、三级业务线是可选字段，用于更细粒度的分析
- 行业组织信息不再作为独立概念，其信息合并到业务线的描述中

### 7.7 环境
| **用户说的** | **environment实际值** |
| --- | --- |
| 生产环境 | R |
| 预发环境 | P |


### 7.8 时间范围
| 用户说的 | dt 条件 |
| --- | --- |
| 今天 / 昨天 | dt = '${bizdate}' |
| 最近7天 | dt >= DATE_FORMAT(DATEADD('{bizdate}', -6, 'dd'), 'yyyyMMdd') AND dt <= '{bizdate}' |
| 过去30天 | dt >= DATE_FORMAT(DATEADD('{bizdate}', -29, 'dd'), 'yyyyMMdd') AND dt <= '{bizdate}' |


---

## 八、通用查询样例
> **重要：** 所有 SQL 必须加表前缀，ADS表必须加 `AND environment = 'R'`
>

### 8.1 按业务线统计push任务（DWD宽表，推荐）
```sql
-- 按一级业务线统计任务数和运行中任务数
SELECT 
    dt
        ,biz_line_name_lv1
        ,COUNT(DISTINCT delivery_push_task_id) AS total_task_cnt
        ,COUNT(DISTINCT CASE WHEN status = 'RUNNING' THEN delivery_push_task_id END) AS running_task_cnt
FROM    adm_hk_asap_dwd_push_task_info_dd
WHERE   dt = '${bizdate}'
AND     environment = 'R'
AND     business_unit_code = 'SG_MAGA_HK'
GROUP BY dt
        ,biz_line_name_lv1
ORDER BY total_task_cnt DESC;
```

### 8.2 按业务线分类统计（DWD宽表）
```sql
-- 统计一级、二级、三级业务线下的任务分布
SELECT 
    dt,
        biz_line_name_lv1,
        biz_line_name_lv2,
        biz_line_name_lv3,
        COUNT(DISTINCT delivery_push_task_id) AS task_cnt,
        COUNT(DISTINCT CASE WHEN creative_type = 'AIGC' THEN delivery_push_task_id END) AS aigc_task_cnt
FROM    adm_hk_asap_dwd_push_task_info_dd
WHERE   dt = '${bizdate}'
AND     environment = 'R'
AND     business_unit_code = 'SG_MAGA_HK'
GROUP BY dt
        ,biz_line_name_lv1
        ,biz_line_name_lv2
        ,biz_line_name_lv3
ORDER BY task_cnt DESC;
```

### 8.3 push发送效果汇总（ADS快表）
```sql
SELECT  dt
        ,biz_line_name_lv1
        ,SUM(send_cnt_pv)                  AS send_total_pv
        ,SUM(send_success_cnt_pv)           AS send_success_pv
        ,SUM(exposure_pv)                  AS exposure_total_pv
        ,SUM(click_pv)                     AS click_total_pv
        ,ROUND(SUM(click_pv) / NULLIF(SUM(exposure_pv), 0), 4) AS pv_ctr
        ,SUM(send_cnt_uv)                  AS send_total_uv
        ,SUM(exposure_uv)                  AS exposure_total_uv
        ,SUM(click_uv)                     AS click_total_uv
        ,ROUND(SUM(click_uv) / NULLIF(SUM(exposure_uv), 0), 4) AS uv_ctr
FROM    adm_hk_asap_push_task_info_fast_ds
WHERE   dt = '${bizdate}'
  AND     environment = 'R'
GROUP BY dt
        ,biz_line_name_lv1
ORDER BY click_total_pv DESC;
```

### 8.4 业务线维度下AIGC任务分析
```sql
-- 分析各业务线的AIGC任务占比、创新情况
SELECT 
    biz_line_name_lv1,
    COUNT(DISTINCT delivery_push_task_id)                     AS total_task_cnt,
    SUM(CASE WHEN creative_type = 'AIGC' THEN 1 ELSE 0 END)        AS aigc_task_cnt,
    ROUND(aigc_task_cnt * 1.0 / NULLIF(total_task_cnt, 0), 4) AS aigc_task_ratio
FROM    adm_hk_asap_dwd_push_task_info_dd
WHERE   dt = '${bizdate}'
AND     environment = 'R'
GROUP BY biz_line_name_lv1
ORDER BY total_task_cnt DESC;
```

---

## 九、查询注意事项
1. **分区字段**：dt 格式为 `yyyyMMdd`，如 `20260319`
2. **environment过滤**：ADS表查询必须加 `AND environment = 'R'`，否则会包含预发数据
3. **核心DWD表**：`adm_hk_asap_dwd_push_task_info_dd`是查询任务维度的核心表，包含所有push任务、文案、业务线等信息
4. **业务线优先**：业务线是push域的核心组织维度，所有查询都应该按业务线分组，便于业务线负责的数据管理
5. **用户级明细表**：`adm_hk_asap_dwd_push_send_expo_clk_detail_fast/slow_di` 提供按任务和用户的详细效果分析
6. **AIGC任务表**：`adm_asap_push_aigc_task_running_dd` 记录AIGC专用任务信息，用于AI效果分析
7. **空值处理**：除法运算统一使用 `NULLIF(分母, 0)` 避免除零错误
8. **快慢表区分**：
    - 快表：T+5分钟延迟
    - 慢表：T+2小时延迟
9. **业务线多级结构**：使用一级、二级、三级业务线结构，满足不同分析粒度需求
10. **任务状态判断**：任务状态包括INIT(初始)、RUNNING(运行中)、PAUSE(暂停)、FINISH(完成)
