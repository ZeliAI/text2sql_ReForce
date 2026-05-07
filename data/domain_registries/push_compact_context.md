# push域 Compact Schema Context

## 全局规则
- JOIN 规则：优先使用 ADS / DWS 汇总表；任务详情使用核心 DWD 宽表；曝光/点击明细按 delivery_push_task_id 关联任务表。
- dt 规则：所有 push 域查询必须过滤 dt 分区；线上环境优先补充 environment = 'R'。

## 表与字段
### antsg_anthk_sg.adm_hk_asap_dwd_push_task_info_dd
- 层级：DWD（明细层）
- 用途：push任务核心宽表，汇总所有任务、文案、业务线、AIGC文案等所有信息
- 字段：dt（日期）、delivery_push_task_id（push任务ID）、creative_id（文案ID）、industry_org_id（行业组织ID）、push_type（push类型）、creative_type（文案类型）、status（任务状态）、user_id（用户ID）、push_channel_type（push渠道类型）、environment（环境）、business_unit_code（业务单元编码）、biz_line_name_lv1（一级业务线名称）、biz_line_name_lv2（二级业务线名称）、biz_line_name_lv3（三级业务线名称）、industry_org_name（行业组织名称）、gmt_create（创建时间）、gmt_modified（修改时间）、call_login（负责工号）、aigc_text（AIGC生成文案）

### antsg_anthk_sg.adm_hk_asap_dwd_push_send_expo_clk_detail_slow_di
- 层级：DWS（明细层）
- 用途：push慢表，用于分析push消息的发送曝光及点击转化效果，聚焦慢查询场景
- 字段：delivery_push_task_id（push任务ID）、delivery_push_task_name（push任务名称）、industry_org_id（行业组织ID）、industry_org_name（行业组织名称）、creative_id（文案ID）、creative_type（文案类型）、creative_tag（文案标签）、send_time（发送时间-时间戳）、send_date（发送时间-东八区）、user_id（用户ID）、send_status（push任务发送状态）、send_fail_msg（push任务失败原因）、push_title（push标题）、push_sub_title（push副标题）、push_url（push URL）、model（机型，ANDROID/IOS）、user_lifecycle（用户生命周期）、user_value（用户价值）、user_activity_level（用户活跃分层）、push_type（push类型）、push_task_start_date（push任务开始时间）、push_task_end_date（push任务结束时间）、push_task_gmt_create（push任务创建时间）、is_expo（是否曝光，1是0否）、expo_pv（曝光次数）、is_clk（是否点击，1是0否）、clk_pv（点击次数）、dt（日期分区）、is_expo（是否曝光）、expo_pv（曝光次数）、is_clk（是否点击）、clk_pv（点击次数）

### antsg_anthk_sg.adm_hk_asap_push_task_info_detail_di
- 层级：DWD（明细层）
- 用途：push发送日志明细表，记录每个用户/设备的发送记录
- 字段：dt（日期）、delivery_push_task_id（push任务ID）、user_id（用户ID）、service_code（service_code）、creative_id（文案ID）、send_time（发送时间）、send_status（发送状态）、send_fail_msg（失败原因）、push_title（文案标题）、push_sub_title（文案副标题）、push_url（文案URL）、business_unit_code（业务单元代码）、environment（环境）、msg_id（msg_id）、extend_info（扩展字段）、tnt_id（租户id）、send_count（发送次数）、send_success_count（发送成功次数）、send_fail_count（发送失败次数）

### antsg_anthk_sg.adm_hk_asap_dwd_push_log_expo_di
- 层级：DWD（明细层）
- 用途：push域曝光日志明细表，用于分析push消息的曝光效果
- 字段：loged_time（上传服务器记录时间）、log_time（客户端日志时间）、alipay_product_id（产品ID）、alipay_product_version（产品版本）、tcid（设备id）、session_id（会话id）、user_id（用户id(2088开头)）、behaviorid（行为id(exposure)）、spm（曝光点的spm）、spm_a（曝光点spm的a位）、spm_b（曝光点spm的b位）、spm_c（曝光点spm的c位）、spm_d（曝光点spm的d位）、utdid（utdid）、device_model（设备号）、os_version（操作系统版本）、network（网络）、language（语言）、ip（ip）、ip_country（从ip中解析出来的国家名称）、ip_province（从ip中解析出来的省份名称）、ip_city（从ip中解析出来的城市名称）、log_type（日志来源渠道）、experiment_ids（ABTest的实验id）、msg_id（ifcgotone的msgId）、delivery_push_task_id（push任务ID）、service_code（service code）、creative_id（文案ID）、push_title（push的标题）、push_sub_title（push的文本）、push_url（push的uri,json格式）、dt（时间分区）

### antsg_anthk_sg.adm_hk_asap_dwd_push_log_clk_di
- 层级：DWD（明细层）
- 用途：push域点击日志明细表，用于分析push消息的点击转化效果
- 字段：loged_time（上传服务器记录时间）、log_time（客户端日志时间）、alipay_product_id（产品ID）、alipay_product_version（产品版本）、tcid（设备id）、session_id（会话id）、user_id（用户id(2088开头)）、behaviorid（行为id(clicked)）、spm（当前点击的spm）、spm_a（当前点击spm的a位）、spm_b（当前点击spm的b位）、spm_c（当前点击spm的c位）、spm_d（当前点击spm的d位）、utdid（utdid）、device_model（设备号）、os_version（操作系统版本）、network（网络）、language（语言）、ip（ip）、ip_country（从ip中解析出来的国家名称）、ip_province（从ip中解析出来的省份名称）、ip_city（从ip中解析出来的城市名称）、log_type（日志来源渠道）、experiment_ids（ABTest的experimentIds）、msg_id（ifcgotone的msgId）、delivery_push_task_id（push任务ID）、service_code（service code）、creative_id（文案ID）、push_title（push的标题）、push_sub_title（push的文本）、push_url（push的uri,json格式）、dt（时间分区）

## 常用业务术语映射
- 营销Push -> push_type = 'PUSH_MARKETING'
- 平台Push -> push_type = 'PUSH_PLATFORM'
- 策略Push -> push_type = 'PUSH_STRATEGY'
- 商业化Push -> push_type = 'PUSH_COMMERCIAL'
- 事件Push -> push_type = 'PUSH_EVENT'
- 人工文案 -> creative_type = 'MANUAL / 空'
- AIGC文案 -> creative_type = 'LLM / AIGC'
- 大模型文案 -> creative_type = 'LLM / AIGC'
- 规则引擎 -> creative_type = 'RULE'
- 标签引擎 -> creative_type = 'LABEL'
- 利益导向 -> creative_tag = 'Benefit_Oriented'
- 情感导向 -> creative_tag = 'Emotion_Oriented'
- 紧急导向 -> creative_tag = 'Urgency_Oriented'
- 任务初始 -> status = 'INIT'
- 任务运行中/生效中 -> status = 'RUNNING'
- 任务暂停 -> status = 'PAUSE'
- 任务完成 -> status = 'FINISH'
- 自动触发 -> push_trigger_type = 'auto'
- 人工触发 -> push_trigger_type = 'manual'
- 算法触发 -> push_trigger_type = 'alg'
- 生产环境 -> environment = 'R'
- 预发环境 -> environment = 'P'
- 今天 / 昨天 -> dt = '${bizdate}'
- 最近7天 -> dt >= DATE_FORMAT(DATEADD('{bizdate}', -6, 'dd'), 'yyyyMMdd') AND dt <= '{bizdate}'
- 过去30天 -> dt >= DATE_FORMAT(DATEADD('{bizdate}', -29, 'dd'), 'yyyyMMdd') AND dt <= '{bizdate}'

## 核心概念
- Push任务：push任务，控制投放时间、范围、内容等；关联表：**adm_hk_asap_dwd_push_task_info_dd** (核心DWD宽表，汇总所有任务、文案、业务线、行业组织、AIGC文案等所有信息)
- Push文案：push文案，包含标题、副标题、URL等；关联表：antsg_nods.ods_imcdp_static_content
- Push发送：消息发送到设备；关联表：anthk_sg.dwd_intl_gloc_hk_push_out_history_750_dd
- Push曝光：消息在设备上展示；关联表：anthk_sg.dwd_evt_hk_app_log_exposure_di
- Push点击：用户点击push消息；关联表：anthk_sg.dwd_evt_hk_app_log_clk_di
- 业务线：业务分类维度，用于组织投放资源；关联表：antsg_nods.ods_imcdp_biz_line_org
- AIGC文案：大模型生成的push文案；关联表：ods_imcdp_static_content.extend_info.llmPushTextParam

## 选表规则
- 查发送量/曝光量/点击量/CTR等聚合指标（任务维度） -> **ADS** adm_hk_asap_push_task_info_fast/slow_ds；原因：已按天汇总，性能最优
- 查push任务详情/文案信息/任务状态/业务线 -> **DWD** adm_hk_asap_dwd_push_task_info_dd；原因：核心宽表，包含所有维度信息；业务线作为关键的组织维度，包含一级、二级、三级等多级结构
- 需要用户级（单个用户）的发送/曝光/点击明细 -> **DWS** adm_hk_asap_dwd_push_send_expo_clk_detail_fast/slow_di；原因：汇总层有用户级数据
- AIGC任务分析（running状态/任务类型） -> **DWD** adm_asap_push_aigc_task_running_dd；原因：专用AIGC任务表
- AIGC流量分析（累计指标/创意效果对比） -> **ADS** adm_asap_push_aigc_trfc_analysis_di；原因：专用AIGC流量表
- 曝光/点击日志明细分析 -> **DWD** adm_hk_asap_dwd_push_log_expo_di / log_clk_di；原因：明细层日志表

## 指标口径
- 发送量PV：SUM(send_cnt_pv)；push消息发送总数
- 发送成功量PV：SUM(send_success_cnt_pv)；push成功发送到设备数
- 曝光量PV：SUM(exposure_pv)；push消息在设备上的展示次数
- 点击量PV：SUM(click_pv)；用户点击push消息次数
- 发送量UV：SUM(send_cnt_uv)；发送给不同用户的数量
- 曝光量UV：SUM(exposure_uv)；不同用户看到push消息的数量
- 点击量UV：SUM(click_uv)；不同用户点击push消息的数量
- PV CTR：SUM(click_pv) / NULLIF(SUM(exposure_pv), 0)；点击PV / 曝光PV，保留4位小数
- UV CTR：SUM(click_uv) / NULLIF(SUM(exposure_uv), 0)；点击UV / 曝光UV，保留4位小数
- 总任务数：COUNT(DISTINCT delivery_push_task_id)；push任务总数
- 运行中任务数：COUNT(DISTINCT CASE WHEN status = 'RUNNING' THEN delivery_push_task_id END)；当前运行中的任务数
- 按业务线统计：COUNT(DISTINCT CASE WHEN biz_line_code_lv1 = 'xxx' THEN delivery_push_task_id END)；按一级业务线统计任务数
- 用户级曝光计数：SUM(expo_count)；某用户某任务的曝光次数
- 用户级点击计数：SUM(clk_count)；某用户某任务的点击次数
- 用户级CTR：SUM(clk_count) / NULLIF(SUM(expo_count), 0)；用户级点击率
