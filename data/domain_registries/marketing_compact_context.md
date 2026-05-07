# 投放域 Compact Schema Context

## 全局规则
- JOIN 规则：优先使用 DWS 汇总表；仅当需要用户级明细或明细字段时使用 DWD，并按业务外键关联 DIM 表。
- dt 规则：所有投放域查询必须过滤 dt 分区；线上环境优先补充 environment = 'R'。

## 表与字段
### anthk_sg.dws_hk_asap_mkt_distribute_index_1d
- 层级：DWS（汇总层）
- 用途：投放曝光点击轻度汇总表
- 字段：dt（日期分区）、space_id（展位ID）、space_code（展位CODE）、space_name（展位名称）、delivery_task_id（投放任务ID）、delivery_task_name（投放任务名称）、industry_org_id（行业ID）、industry_org_name（行业名称）、content_id（投放内容ID / 供给ID / 商户ID）、title（投放内容标题 / 供给名称 / 商户名称）、content_type（内容类型）、traffic_type（流量类型）、user_id（用户ID（计算UV时使用））、slot_id（坑位ID）、is_public（是否公域展位）、delivery_task_status（投放任务状态）、environment（环境标识）、expo_pv_1d（曝光PV / 流量消耗）、clk_pv_1d（点击PV）、expo_uv（计算指标）（曝光UV）、clk_uv（计算指标）（点击UV）、pv_ctr（计算指标）（PV点击率）、uv_ctr（计算指标）（UV点击率）

### antsg_anthk_sg.dwd_hk_asap_mkt_log_expo_di
- 层级：DWD（明细层）
- 用途：投放域曝光日志日增明细表，用于按用户/事件追踪曝光行为
- 字段：loged_time（上传服务器记录时间）、log_time（客户端日志时间）、alipay_product_id（产品ID）、alipay_product_version（产品版本）、tcid（设备id）、session_id（会话id）、user_id（用户id(2088开头)）、behaviorid（行为id(exposure)）、spm（曝光点的spm）、spm_a（曝光点spm的a位）、spm_b（曝光点spm的b位）、spm_c（曝光点spm的c位）、spm_d（曝光点spm的d位）、utdid（utdid）、device_model（设备号）、os_version（操作系统版本）、network（网络）、language（语言）、ip（ip）、ip_country（从ip中解析出来的国家名称）、ip_province（从ip中解析出来的省份名称）、ip_city（从ip中解析出来的城市名称）、log_type（日志来源渠道）、experiment_ids（ABTest的实验id）、space_code（展位code）、space_name（展位名称）、delivery_task_id（投放任务ID）、delivery_task_name（投放任务名称）、industry_org_id（行业ID）、industry_org_name（行业名称）、content_id（投放内容ID）、title（投放内容标题）、content_type（投放内容类型）、traffic_type（流量类型）、slot_id（坑位ID）、is_public（是否公域展位）、delivery_task_status（投放任务状态）、dt（时间分区）

### antsg_anthk_sg.dwd_hk_asap_mkt_log_clk_di
- 层级：DWD（明细层）
- 用途：投放域点击日志日增明细表，用于按用户/事件追踪点击行为
- 字段：loged_time（上传服务器记录时间）、log_time（客户端日志时间）、alipay_product_id（产品ID）、alipay_product_version（产品版本）、tcid（设备id）、session_id（会话id）、user_id（用户id(2088开头)）、behaviorid（行为id(clicked)）、spm（当前点击的spm）、spm_a（当前点击spm的a位）、spm_b（当前点击spm的b位）、spm_c（当前点击spm的c位）、spm_d（当前点击spm的d位）、utdid（utdid）、device_model（设备号）、os_version（操作系统版本）、network（网络）、language（语言）、ip（ip）、ip_country（从ip中解析出来的国家名称）、ip_province（从ip中解析出来的省份名称）、ip_city（从ip中解析出来的城市名称）、log_type（日志来源渠道）、experiment_ids（ABTest的experimentIds）、space_code（展位code）、space_name（展位名称）、delivery_task_id（投放任务ID）、delivery_task_name（投放任务名称）、industry_org_id（行业ID）、industry_org_name（行业名称）、content_id（投放内容ID）、title（投放内容标题）、content_type（投放内容类型）、traffic_type（流量类型）、slot_id（坑位ID）、is_public（是否公域展位）、delivery_task_status（投放任务状态）、dt（时间分区）

### antsg_anthk_sg.dim_hk_asap_mkt_delivery_task_dd
- 层级：DIM（维度层）
- 用途：投放任务维度表，存储投放任务的配置信息和状态
- 字段：delivery_task_id（投放任务ID）、delivery_task_name（投放任务名称）、delivery_task_status（投放任务状态）、space_id（展位ID）、space_code（展位CODE）、space_name（展位名称）、industry_org_id（行业ID）、industry_org_name（行业名称）、traffic_type（流量类型）、is_public（是否公域展位）、start_time（投放开始时间）、end_time（投放结束时间）、gmt_create（创建时间）、gmt_modified（修改时间）、environment（环境标识）、dt（日期分区）

### antsg_anthk_sg.dim_hk_asap_space_info_dd
- 层级：DIM（维度层）
- 用途：展位信息维度表，存储展位的配置信息和属性
- 字段：space_id（展位ID）、space_code（展位CODE）、space_name（展位名称）、space_status（展位状态）、industry_org_id（行业ID）、industry_org_name（行业名称）、is_public（是否公域展位）、space_type（展位类型）、gmt_create（创建时间）、gmt_modified（修改时间）、environment（环境标识）、dt（日期分区）

### antsg_anthk_sg.dim_hk_asap_content_dd
- 层级：DIM（维度层）
- 用途：内容维度表，存储投放内容的配置信息和属性
- 字段：content_id（投放内容ID）、title（投放内容标题）、content_type（内容类型）、content_status（内容状态）、content_url（内容链接）、gmt_create（创建时间）、gmt_modified（修改时间）、environment（环境标识）、dt（日期分区）

### antsg_anthk_sg.dim_hk_asap_industry_info_dd
- 层级：DIM（维度层）
- 用途：行业信息维度表，存储行业组织架构和分类信息
- 字段：industry_org_id（行业ID）、industry_org_name（行业名称）、parent_industry_org_id（父级行业ID）、industry_level（行业层级）、industry_status（行业状态）、gmt_create（创建时间）、gmt_modified（修改时间）、environment（环境标识）、dt（日期分区）

## 常用业务术语映射
- 竞争流量 -> WHERE traffic_type = 'NON_COMMERCIAL_COMPETITIVE'
- 商业化流量 -> WHERE traffic_type = 'COMMERCIAL'
- 预算流量 -> WHERE traffic_type = 'NON_COMMERCIAL_BUDGET'
- 公域展位 -> WHERE is_public = 1
- 非公域展位 -> WHERE is_public = 0
- N号坑位 / 第N个位置 -> WHERE slot_id = N
- 大盘整体（线上数据） -> 无需 space 过滤，必须加 AND environment = 'R'
- 今天 / 昨天 -> dt = '${bizdate}'
- 最近7天 -> dt >= DATE_FORMAT(DATEADD('${bizdate}', -6, 'dd'), 'yyyyMMdd') AND dt <= '${bizdate}'
- 过去30天 -> dt >= DATE_FORMAT(DATEADD('${bizdate}', -29, 'dd'), 'yyyyMMdd') AND dt <= '${bizdate}'
- 上周 -> dt BETWEEN 上周一 AND 上周日
- 周同比 -> dt IN ('${bizdate}', DATE_FORMAT(DATEADD('${bizdate}', -7, 'dd'), 'yyyyMMdd'))

## 核心概念
- 展位：投放位置，如首页Banner、弹窗、列表卡片等；关联表：anthk_sg.dim_hk_asap_space_info_dd
- 内容：投放物料，如图片、活动、权益、商品等；关联表：anthk_sg.dim_hk_asap_content_dd
- 任务：投放任务，控制投放时间、范围、内容等；关联表：anthk_sg.dim_hk_asap_mkt_delivery_task_dd
- 行业：业务分类维度，用于组织投放资源；关联表：anthk_sg.dim_hk_asap_industry_info_dd
- 坑位：内容曝光的位置编号；关联表：anthk_sg.dws_hk_asap_mkt_distribute_index_1d

## 选表规则
- 查曝光PV/点击PV/UV/CTR/日均/趋势/同比 -> **DWS** anthk_sg.dws_hk_asap_mkt_distribute_index_1d；原因：已按天汇总，性能最优
- 按展位/任务/行业/内容/流量类型/坑位分组 -> **DWS** anthk_sg.dws_hk_asap_mkt_distribute_index_1d；原因：包含所有聚合维度
- 查展位/任务/内容/行业的属性、名称 -> **DIM** 对应维度表；原因：维度信息在 DIM 层
- 需要 experiment_ids、utdid -> **DWD** anthk_sg.dwd_hk_asap_mkt_log_expo/clk_di；原因：仅明细层有
- 需要事件级（每次曝光/点击）明细 -> **DWD** anthk_sg.dwd_hk_asap_mkt_log_expo/clk_di；原因：仅明细层有
- user_id + experiment_id 联合分析 -> **DWD** anthk_sg.dwd_hk_asap_mkt_log_expo/clk_di；原因：仅明细层有

## 指标口径
- 曝光PV：SUM(expo_pv_1d)；按天汇总的曝光次数
- 点击PV：SUM(clk_pv_1d)；按天汇总的点击次数
- 曝光UV：COUNT(DISTINCT CASE WHEN expo_pv_1d > 0 THEN user_id END)；去重曝光用户数
- 点击UV：COUNT(DISTINCT CASE WHEN clk_pv_1d > 0 THEN user_id END)；去重点击用户数
- PV CTR：SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0)；点击PV / 曝光PV，保留4位小数
- UV CTR：点击UV / NULLIF(曝光UV, 0)；点击UV / 曝光UV
- 日均PV CTR：SUM(clk_pv_1d) / NULLIF(SUM(expo_pv_1d), 0) / COUNT(DISTINCT dt)；多日区间内日均点击率
- 人均曝光：SUM(expo_pv_1d) / NULLIF(曝光UV, 0)；平均每人曝光次数
- 展位数：COUNT(DISTINCT space_id)；有效展位数
- 任务数：COUNT(DISTINCT delivery_task_id)；投放任务数
- 曝光PV：COUNT(*) FROM dwd_hk_asap_mkt_log_expo_di
- 点击PV：COUNT(*) FROM dwd_hk_asap_mkt_log_clk_di
- 曝光UV：COUNT(DISTINCT user_id) FROM dwd_hk_asap_mkt_log_expo_di
- 点击UV：COUNT(DISTINCT user_id) FROM dwd_hk_asap_mkt_log_clk_di
- PV CTR：点击PV / NULLIF(曝光PV, 0)
- UV CTR：点击UV / NULLIF(曝光UV, 0)
