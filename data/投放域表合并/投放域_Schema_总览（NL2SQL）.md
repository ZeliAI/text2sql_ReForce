# 投放域 Schema 总览（NL2SQL）

> 本文档为投放域 Schema 元数据总览，包含域说明、表索引、选表规则、**指标口径**、业务术语映射、通用取数样例。各表字段详情见关联文档。
>
> **原则：SKILL.md 只记录域注册信息，完整 Schema 从本语雀文档按需拉取。**  
拉取方式：`yuque-mcp skylark_user_doc_detail`，命名空间 `gaespg/tkz7r8`，slug `aqxsx8at4mtg54i2`

---

## 一、域说明
投放域覆盖营销投放业务，包含展位、内容投放、效果追踪等核心场景。

**业务范围：**

- 展位效果：曝光、点击、转化等指标分析
- 内容效果：曝光、点击、转化等指标分析
- 任务效果：曝光、点击、转化等指标分析

---

## 二、核心概念
| **概念** | **英文** | **说明** | **关联表** |
| --- | --- | --- | --- |
| 展位 | Space | 投放位置，如首页Banner、弹窗、列表卡片等 | anthk_sg.dim_hk_asap_space_info_dd |
| 内容 | Content | 投放物料，如图片、活动、权益、商品等 | anthk_sg.dim_hk_asap_content_dd |
| 任务 | Task | 投放任务，控制投放时间、范围、内容等 | anthk_sg.dim_hk_asap_mkt_delivery_task_dd |
| 行业 | Industry | 业务分类维度，用于组织投放资源 | anthk_sg.dim_hk_asap_industry_info_dd |
| 坑位 | slot_id | 内容曝光的位置编号 | anthk_sg.dws_hk_asap_mkt_distribute_index_1d |

---

## 三、表层级关系
```plain
┌──────────────────────────────────────────────────────────┐
│                       DWS 汇总层                          │
│         dws_hk_asap_mkt_distribute_index_1d              │
│         （按天汇总，曝光PV/点击PV/UV/CTR 等）              │
└──────────────────────────────────────────────────────────┘
                          ▲（汇总自）
┌──────────────────────────────────────────────────────────┐
│                       DWD 明细层                          │
│  dwd_hk_asap_mkt_log_expo_di（曝光明细）                  │
│  dwd_hk_asap_mkt_log_clk_di（点击明细）                   │
└──────────────────────────────────────────────────────────┘
                          ▲（关联）
┌──────────────────────────────────────────────────────────┐
│                       DIM 维度层                          │
│  dim_delivery_task  dim_space  dim_content  dim_industry  │
└──────────────────────────────────────────────────────────┘
```

---

## 四、表索引
| 表名 | 层级 | 主键 | 核心外键 | 说明 | 详情文档 |
| --- | --- | --- | --- | --- | --- |
| anthk_sg.dws_hk_asap_mkt_distribute_index_1d | DWS | space_code, delivery_task_id, content_id | space_code, content_id, delivery_task_id, industry_org_id | 流量分发指标日增汇总表（**优先使用**） | [查看](./投放域_02_dws_hk_asap_mkt_distribute_index_1d.md) |
| anthk_sg.dwd_hk_asap_mkt_log_expo_di | DWD | space_code, user_id, content_id | space_code, content_id, delivery_task_id, industry_org_id | 曝光日志日增明细表 | [查看](./投放域_03_dwd_hk_asap_mkt_log_expo_di.md) |
| anthk_sg.dwd_hk_asap_mkt_log_clk_di | DWD | space_code, user_id, content_id | space_code, content_id, delivery_task_id, industry_org_id | 点击日志日增明细表 | [查看](./投放域_04_dwd_hk_asap_mkt_log_clk_di.md) |
| anthk_sg.dim_hk_asap_mkt_delivery_task_dd | DIM | delivery_task_id | space_id, industry_org_id | 投放任务维度表 | [查看](./投放域_05_dim_hk_asap_mkt_delivery_task_dd.md) |
| anthk_sg.dim_hk_asap_space_info_dd | DIM | space_id | industry_org_id | 展位信息维度表 | [查看](./投放域_06_dim_hk_asap_space_info_dd.md) |
| anthk_sg.dim_hk_asap_content_dd | DIM | content_id | content_id | 内容维度表 | [查看](./投放域_07_dim_hk_asap_content_dd.md) |
| anthk_sg.dim_hk_asap_industry_info_dd | DIM | industry_org_id | tnt_id | 行业信息维度表 | [查看](./投放域_08_dim_hk_asap_industry_info_dd.md) |

---

## 五、选表规则（NL2SQL 核心）
**核心原则：DWS 优先，明细字段才降级 DWD。**

| 场景 | 使用表 | 理由 |
| --- | --- | --- |
| 查曝光PV/点击PV/UV/CTR/日均/趋势/同比 | **DWS** anthk_sg.dws_hk_asap_mkt_distribute_index_1d | 已按天汇总，性能最优 |
| 按展位/任务/行业/内容/流量类型/坑位分组 | **DWS** anthk_sg.dws_hk_asap_mkt_distribute_index_1d | 包含所有聚合维度 |
| 查展位/任务/内容/行业的属性、名称 | **DIM** 对应维度表 | 维度信息在 DIM 层 |
| 需要 experiment_ids、utdid | **DWD** anthk_sg.dwd_hk_asap_mkt_log_expo/clk_di | 仅明细层有 |
| 需要事件级（每次曝光/点击）明细 | **DWD** anthk_sg.dwd_hk_asap_mkt_log_expo/clk_di | 仅明细层有 |
| user_id + experiment_id 联合分析 | **DWD** anthk_sg.dwd_hk_asap_mkt_log_expo/clk_di | 仅明细层有 |


```plain
判断流程：
用户需求
  → 包含 experiment_ids / utdid / 事件级明细？
      是 → 使用 DWD
      否 → 使用 DWS（优先）
```

---

## 六、指标口径（NL2SQL 核心）
### 6.1 DWS 口径（优先使用）
> 基于 `anthk_sg.dws_hk_asap_mkt_distribute_index_1d`，查询时必须加 `AND environment = 'R'`

| 指标名称 | DWS 计算公式 | 说明 |
| --- | --- | --- |
| 曝光PV | SUM(expo_pv_1d) | 按天汇总的曝光次数 |
| 点击PV | SUM(clk_pv_1d) | 按天汇总的点击次数 |
| 曝光UV | COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END) | 去重曝光用户数 |
| 点击UV | COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END) | 去重点击用户数 |
| PV CTR | SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0) | 点击PV / 曝光PV，保留4位小数 |
| UV CTR | 点击UV / NULLIF(曝光UV, 0) | 点击UV / 曝光UV |
| 日均PV CTR | SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0) / COUNT(DISTINCT dt) | 多日区间内日均点击率 |
| 人均曝光 | SUM(expo_pv_1d) / NULLIF(曝光UV, 0) | 平均每人曝光次数 |
| 展位数 | COUNT(DISTINCT space_id) | 有效展位数 |
| 任务数 | COUNT(DISTINCT delivery_task_id) | 投放任务数 |


### 6.2 DWD 口径（降级使用，DWS 无法满足时）
> 基于 `anthk_sg.dwd_hk_asap_mkt_log_expo_di` / `anthk_sg.dwd_hk_asap_mkt_log_clk_di`

| 指标名称 | DWD 计算公式 |
| --- | --- |
| 曝光PV | COUNT(*) FROM dwd_hk_asap_mkt_log_expo_di |
| 点击PV | COUNT(*) FROM dwd_hk_asap_mkt_log_clk_di |
| 曝光UV | COUNT(DISTINCT user_id) FROM dwd_hk_asap_mkt_log_expo_di |
| 点击UV | COUNT(DISTINCT user_id) FROM dwd_hk_asap_mkt_log_clk_di |
| PV CTR | 点击PV / NULLIF(曝光PV, 0) |
| UV CTR | 点击UV / NULLIF(曝光UV, 0) |


---

## 七、业务术语映射（NL2SQL 核心）
### 7.1 流量类型
| **用户说的** | **SQL 写法** |
| --- | --- |
| 竞争流量 | WHERE traffic_type = 'NON_COMMERCIAL_COMPETITIVE' |
| 商业化流量 | WHERE traffic_type = 'COMMERCIAL' |
| 预算流量 | WHERE traffic_type = 'NON_COMMERCIAL_BUDGET' |
| 公域展位 | WHERE is_public = 1 |
| 非公域展位 | WHERE is_public = 0 |
| N号坑位 / 第N个位置 | WHERE slot_id = N |
| 大盘整体（线上数据） | 无需 space 过滤，必须加 AND environment = 'R' |


### 7.2 展位口语名称
展位口语名称 → space_name 实际值

| 口语描述 | space_name 实际值 |
| --- | --- |
| 腰封/首页banner | 首页Banner样式A展位 |
| 首页feeds | 首页feeds |
| 支付结果页 | HK支付结果页-综合推荐展位 |
| 卡片角标 | HK积分卡片角标 |
| 积分 | HK积分阵地精选区域模板 |
| 频道角标 | HK首页频道角标 |
| 积分氛围 | 基础积分任务列表展位 |
| 金刚位 | HK首页底部金刚位角标 |
| 服务卡点 | HK首页服务卡片展位 |
| 积分阵地 | HK积分阵地tab角标展位 |
| 生活频道 | 生活频道主tab |
| 本地优惠 | 本地优惠banner |
| 金融阵地 | 金融阵地投承一体_Banner |
| 海外feeds | 海外版首页feeds |
| 票务feeds | 票务feeds |
| 易乘码页面腰封 | 易乘码页面-腰封Banner |
| 支付结果页商户卡片 | 支付结果页-商户服务卡片展位 |
| 生活跨境 | 生活跨境推荐服务展位 |
| 票务阵地 | 票务阵地 |
| 数娱feeds | 数娱feeds |
| 滴滴打车腰封 | 滴滴打车-腰封Banner |
| APP闪屏 | APP闪屏投放展位 |
| 同程乘车码 | 同程乘車碼 |
| 充值页综合推荐 | HK充值页综合推荐 |
| 首页定投任务卡片 | 首页-定投任务卡片 |
| 搜索A级活动 | 搜索-A级活动 |


### 7.3 时间范围
| 用户说的 | dt 条件 |
| --- | --- |
| 今天 / 昨天 | dt = '${bizdate}' |
| 最近7天 | dt >= DATE_FORMAT(DATEADD('${bizdate}', -6, 'dd'), 'yyyyMMdd') AND dt <= '${bizdate}' |
| 过去30天 | dt >= DATE_FORMAT(DATEADD('${bizdate}', -29, 'dd'), 'yyyyMMdd') AND dt <= '${bizdate}' |
| 上周 | dt BETWEEN 上周一 AND 上周日 |
| 周同比 | dt IN ('${bizdate}', DATE_FORMAT(DATEADD('${bizdate}', -7, 'dd'), 'yyyyMMdd')) |


---

## 八、通用查询样例
> **重要：** 所有 SQL 必须加表前缀 `anthk_sg.`，DWS 表必须加 `AND environment = 'R'`

### 8.1 展位日曝光点击汇总（DWS，推荐）
```sql
SELECT  dt
        ,space_code
        ,SUM(expo_pv_1d)                                       AS expo_pv
        ,SUM(clk_pv_1d)                                        AS clk_pv
        ,ROUND(SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0), 4) AS pv_ctr
FROM    anthk_sg.dws_hk_asap_mkt_distribute_index_1d
WHERE   dt = '${bizdate}'
AND     environment = 'R'
AND     space_code = 'HK_HOME_PAGE_FEEDS_LIST'
GROUP BY dt
        ,space_code;
```

### 8.2 各行业曝光占比（DWS）
```sql
SELECT  industry_org_name
        ,SUM(expo_pv_1d)                                          AS expo_pv
        ,ROUND(SUM(expo_pv_1d) / SUM(SUM(expo_pv_1d)) OVER (), 4) AS pv_ratio
FROM    anthk_sg.dws_hk_asap_mkt_distribute_index_1d
WHERE   dt = '${bizdate}'
AND     environment = 'R'
GROUP BY industry_org_name
ORDER BY pv_ratio DESC;
```

### 8.3 周同比（DWS）
```sql
SELECT  space_code
        ,SUM(CASE
                    WHEN dt = '${bizdate}' THEN expo_pv_1d
                    ELSE 0
             END) AS today_expo_pv
        ,SUM(CASE
                    WHEN dt = TO_CHAR(DATEADD(TO_DATE('${bizdate}', 'yyyyMMdd'), -7, 'dd'), 'yyyyMMdd') THEN expo_pv_1d
                    ELSE 0
             END) AS last_week_expo_pv
FROM    anthk_sg.dws_hk_asap_mkt_distribute_index_1d
WHERE   dt IN ('${bizdate}', TO_CHAR(DATEADD(TO_DATE('${bizdate}', 'yyyyMMdd'), -7, 'dd'), 'yyyyMMdd'))
AND     environment = 'R'
GROUP BY space_code;
```

### 8.4 关联展位维度（DWD 降级，需明细字段时）
```sql
SELECT  s.space_name
        ,s.space_status
        ,i.industry_org_name
        ,COUNT(*)                  AS expo_pv
        ,COUNT(DISTINCT e.user_id) AS expo_uv
FROM    (
            SELECT  *
            FROM    anthk_sg.dwd_hk_asap_mkt_log_expo_di
            WHERE   dt = '${bizdate}'
        ) e
JOIN    (
            SELECT  *
            FROM    anthk_sg.dim_hk_asap_space_info_dd
            WHERE   dt = '${bizdate}'
        ) s
ON      e.space_id = s.space_id
JOIN    (
            SELECT  *
            FROM    anthk_sg.dim_hk_asap_industry_info_dd
            WHERE   dt = '${bizdate}'
        ) i
ON      e.industry_org_id = i.industry_org_id
GROUP BY s.space_name
        ,s.space_status
        ,i.industry_org_name 
```

### 8.5 CTR 计算（DWS）
```sql
SELECT  space_code
        ,SUM(expo_pv_1d)                                       AS expo_pv
        ,SUM(clk_pv_1d)                                        AS clk_pv
        ,ROUND(SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0), 4) AS pv_ctr
FROM    anthk_sg.dws_hk_asap_mkt_distribute_index_1d
WHERE   dt = '${bizdate}'
AND     environment = 'R'
GROUP BY space_code
ORDER BY pv_ctr DESC 
```

---

## 九、查询注意事项
1. **分区字段必填**：dt 格式为 `yyyyMMdd`，如 `20260319`
2. **environment 过滤**：DWS 表查询必须加 `AND environment = 'R'`，否则会包含预发数据
3. **DWS 优先**：常规曝光点击查询优先走 DWS，性能更优、字段更清晰
4. **空值处理**：除法运算统一使用 `NULLIF(分母, 0)` 避免除零错误
5. **维度表关联**：JOIN 维度表时必须带 `dt` 对齐分区
