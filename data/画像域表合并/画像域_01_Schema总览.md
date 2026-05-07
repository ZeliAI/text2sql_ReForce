# 画像域 Schema 总览（NL2SQL）

---

## 一、表清单
| **层级** | **表名** | **完整路径** | **核心能力** | **何时拉取** | **详情文档** |
| --- | --- | --- | --- | --- | --- |
| ADM | adm_asap_base_user_label_dd | antsg_asap.adm_asap_base_user_label_dd | 用户基础画像（状态/年龄/性别/港漂/注册/认证/设备/LBS/生命周期/价值/风控） | 查询用户属性、人群分层时 | [查看详情](https://yuque.antfin.com/gaespg/tkz7r8/cdrx6umpk9zfsrix) |
| ADM | adm_asap_algo_user_label_dd | anthk_sg.adm_asap_algo_user_label_dd | 用户行为偏好（权益/展位/业务/品类/eM+/基金潜客） | 查询用户偏好、潜客分层时 | [查看详情](https://yuque.antfin.com/gaespg/tkz7r8/qyw4hbm5wm0ggu7e) |
| ADM | adm_asap_pay_user_label_dd | antsg_asap.adm_asap_pay_user_label_dd | 用户交易行为画像（交易频次/金额/场景/支付渠道/退款/用券） | 查询交易特征、消费行为时 | [查看详情](https://yuque.antfin.com/gaespg/tkz7r8/yu5kyeafn39tu5k7) |
| ADM | adm_asap_other_action_user_label_dd | antsg_asap.adm_asap_other_action_user_label_dd | 用户非交易行为画像（活跃/功能使用/浏览/搜索/分享/消息） | 查询活跃度、功能使用时 | [查看详情](https://yuque.antfin.com/gaespg/tkz7r8/ww4bcy09fihm1q4s) |


---

## 二、表关联关系
```plain
adm_asap_base_user_label_dd (user_id, dt)
adm_asap_algo_user_label_dd (user_id, dt)
adm_asap_pay_user_label_dd (user_id, dt)
adm_asap_other_action_user_label_dd (user_id, dt)
```

**关联方式：** 4张表均为平级关系，通过 `user_id` + `dt` 进行 JOIN，均为 1:1。  
**选表原则：查询维度在哪张表，直接用那张表统计，无需强制关联 base 表。** 仅在需要跨表字段组合时才做 JOIN。

---

## 三、选表规则（NL2SQL 核心）
| 查询意图 | 使用表 |
| --- | --- |
| 用户状态/年龄/性别/认证/地区/生命周期/价值/风控 | adm_asap_base_user_label_dd |
| 权益偏好/展位偏好/业务偏好/品类偏好/eM+潜客/基金潜客/回流沉默预警 | adm_asap_algo_user_label_dd |
| 交易频次/交易金额/交易场景/支付渠道/退款/用券 | adm_asap_pay_user_label_dd |
| 活跃度/登录次数/扫码/转账/页面浏览/搜索/push互动 | adm_asap_other_action_user_label_dd |
| 需要跨表字段组合（如：eM+高潜用户的年龄分布） | 各表子查询过滤后 JOIN |


```plain
选表判断流程：
查询所需字段全在一张表？
  是 → 直接单表查询，无需 JOIN
  否 → 各表子查询先过滤 dt + 业务条件，再按 user_id + dt JOIN
```

---

## 四、指标口径（NL2SQL 核心）
### 4.1 用户基础指标（基于 adm_asap_base_user_label_dd）
| 指标名称 | 计算方式 | 说明 |
| --- | --- | --- |
| 用户数 | COUNT(DISTINCT user_id) | 去重用户数 |
| 年龄平均值 | AVG(user_age) WHERE user_age > 0 | 排除 -1（无年龄）的用户 |
| 港漂占比 | COUNT(CASE WHEN is_hk_drifter = 'CX' THEN 1 END) / NULLIF(COUNT(*), 0) | CX = 非永久居民 |
| 女性占比 | COUNT(CASE WHEN user_gender = 'F' THEN 1 END) / NULLIF(COUNT(*), 0) | - |
| 认证率 | COUNT(CASE WHEN new_user_level = 'verified' THEN 1 END) / NULLIF(COUNT(*), 0) | - |
| KYC率 | COUNT(CASE WHEN is_kyc_flag = '1' THEN 1 END) / NULLIF(COUNT(*), 0) | - |
| 高价值用户数 | COUNT(CASE WHEN user_value LIKE '1%' THEN 1 END) | user_value '1' 开头为高价值 |
| 新用户数（新手期） | COUNT(CASE WHEN life_cycle = '1' THEN 1 END) | - |
| 沉默用户数 | COUNT(CASE WHEN life_cycle = '5' THEN 1 END) | - |
| 流失用户数 | COUNT(CASE WHEN life_cycle IN ('6', '61') THEN 1 END) | - |


### 4.2 偏好与潜客指标（基于 adm_asap_algo_user_label_dd）
| 指标名称 | 计算方式 |
| --- | --- |
| 高积分偏好用户数 | COUNT(CASE WHEN pts_prefer_level = 'high' THEN 1 END) |
| 腰封高偏好用户占比 | COUNT(CASE WHEN banner_prefer_level = 'high' THEN 1 END) / NULLIF(COUNT(*), 0) |
| eM+高潜用户数 | COUNT(CASE WHEN em_potential_segment = '高潜' THEN 1 END) |
| eM+高价值用户数 | COUNT(CASE WHEN em_value_user = '1' THEN 1 END) |
| 基金高潜用户数 | COUNT(CASE WHEN fund_potential_segment = '高潜' THEN 1 END) |
| 线上高偏好用户数 | COUNT(CASE WHEN ol_prefer_level = 'high' THEN 1 END) |
| 回流高潜用户数 | COUNT(CASE WHEN reactivation_level = 'high' THEN 1 END) |
| 沉默风险高用户数 | COUNT(CASE WHEN silence_risk_level = 'high' THEN 1 END) |


### 4.3 交易指标（基于 adm_asap_pay_user_label_dd）
| 指标名称 | 计算方式 |
| --- | --- |
| 高频交易用户数 | COUNT(CASE WHEN trx_freq_level_r30d = 'high' THEN 1 END) |
| 高消费用户数 | COUNT(CASE WHEN trx_amt_level_r30d = 'high' THEN 1 END) |
| 平均近30天交易笔均金额 | AVG(avg_trx_amt_r30d) |
| 退款率（平均） | AVG(refund_ratio_r30d) |
| 用券率（平均） | AVG(coupon_usage_ratio_r30d) |
| 线上交易偏好用户占比 | COUNT(CASE WHEN primary_trx_scene_r30d = '线上' THEN 1 END) / NULLIF(COUNT(*), 0) |


### 4.4 活跃度指标（基于 adm_asap_other_action_user_label_dd）
| 指标名称 | 计算方式 |
| --- | --- |
| 月活跃用户数 | COUNT(CASE WHEN is_30d_active = '1' THEN 1 END) |
| 周活跃用户数 | COUNT(CASE WHEN is_7d_active = '1' THEN 1 END) |
| 沉默用户数（30天未活跃） | COUNT(CASE WHEN last_active_days > 30 THEN 1 END) |
| 高活跃用户占比 | COUNT(CASE WHEN active_freq_level_r30d = 'high' THEN 1 END) / NULLIF(COUNT(*), 0) |
| 平均登录次数（近30天） | AVG(login_cnt_r30d) |
| push点击用户数 | COUNT(CASE WHEN is_push_click_user = '1' THEN 1 END) |


---

## 五、业务术语映射（NL2SQL 核心）
### 5.1 用户状态与分层
| 用户说的 | SQL 写法 |
| --- | --- |
| 正常用户 | WHERE user_status = 'T' |
| 注销用户 | WHERE user_status = 'C' |
| 冻结用户 | WHERE user_status = 'B' |
| 新用户（新手期） | WHERE life_cycle = '1' |
| 活跃用户（成长期/成熟期） | WHERE life_cycle IN ('2', '3') |
| 沉默用户（沉默期） | WHERE life_cycle = '5' |
| 流失用户（流失期） | WHERE life_cycle IN ('6', '61') |
| 高价值用户 | WHERE user_value LIKE '1%' OR user_history_value = '高' |
| 低价值用户 | WHERE user_value LIKE '8%' OR user_history_value = '低' |
| 港漂用户 | WHERE is_hk_drifter = 'CX' |
| 本地用户（永久居民） | WHERE is_hk_drifter = 'AX' |
| 菲佣用户 | WHERE is_ph_maid_flag = '1' |
| 已认证用户 | WHERE new_user_level = 'verified' OR is_kyc_flag = '1' |
| 未认证用户 | WHERE new_user_level = 'unverified' |
| 商户用户（收钱码） | WHERE is_pay_qr = '1' |
| 营销黑名单（需排除） | WHERE is_promo_black_flag = '0' AND is_black_list = '0' |


### 5.2 设备与位置
| 用户说的 | SQL 写法 |
| --- | --- |
| iOS用户 | WHERE u_os = 'IOS' OR is_login_ios = '1' |
| 安卓用户 | WHERE u_os = 'ANDROID' OR is_login_android = '1' |
| 英文偏好用户 | WHERE pf_language = 'en_US' OR is_lang_en = '1' |
| 中文偏好用户 | WHERE pf_language IN ('zh_HK', 'zh_Hans') OR is_lang_zh = '1' |
| 内地用户 | WHERE register_number = '86' OR active_region_r30d = '內地' OR is_lbs_cn = '1' |
| 香港用户 | WHERE register_number = '852' OR active_region_r30d = '香港' OR is_lbs_hk = '1' |
| 澳门用户 | WHERE register_number = '853' |


### 5.3 年龄分段
| 用户说的 | SQL 写法 |
| --- | --- |
| 18岁以下 | WHERE user_age_group = '1' OR user_age < 18 |
| 18-25岁 | WHERE user_age_group IN ('2', '3') OR (user_age >= 18 AND user_age <= 25) |
| 26-35岁 | WHERE user_age_group IN ('4', '5') OR (user_age >= 26 AND user_age <= 35) |
| 36-50岁 | WHERE user_age_group IN ('6', '7') OR (user_age >= 36 AND user_age <= 50) |
| 50岁以上 | WHERE user_age_group IN ('8', '9') OR user_age > 50 |
| 年轻用户 | WHERE user_age_group IN ('1', '2', '3', '4') |
| 中年用户 | WHERE user_age_group IN ('5', '6', '7') |
| 老年用户 | WHERE user_age_group IN ('8', '9') |


### 5.4 偏好等级通用映射
| 用户说的 | SQL 写法 |
| --- | --- |
| 高偏好 | WHERE xxx_prefer_level = 'high' |
| 中偏好 | WHERE xxx_prefer_level = 'medium' |
| 低偏好 | WHERE xxx_prefer_level = 'low' |
| 偏好某业务 | WHERE xxx_prefer_level IN ('high', 'medium') |


### 5.5 潜客分层
| 用户说的 | SQL 写法 |
| --- | --- |
| eM+高潜用户 | WHERE em_potential_segment = '高潜' |
| eM+中潜用户 | WHERE em_potential_segment = '中潜' |
| eM+高价值用户 | WHERE em_value_user = '1' |
| eM+营销敏感用户 | WHERE em_marketing_sensitivity = '高营销敏感度' |
| 基金高潜用户 | WHERE fund_potential_segment = '高潜' |
| 回流潜力高用户 | WHERE reactivation_level = 'high' |
| 沉默风险高用户 | WHERE silence_risk_level = 'high' |
| 提频潜力高用户 | WHERE freq_uplift_level = 'high' |


### 5.6 交易行为
| 用户说的 | SQL 写法 |
| --- | --- |
| 高频交易用户 | WHERE trx_freq_level_r30d = 'high' |
| 高消费用户 | WHERE trx_amt_level_r30d = 'high' |
| 线上支付偏好 | WHERE primary_trx_scene_r30d = '线上' OR ol_prefer_level = 'high' |
| 线下支付偏好 | WHERE primary_trx_scene_r30d = '本地线下' OR ll_prefer_level = 'high' |
| 跨境支付偏好 | WHERE primary_trx_scene_r30d = '跨境线下' OR cl_prefer_level = 'high' |
| 缴费偏好用户 | WHERE pt_prefer_level = 'high' OR primary_trx_scene_r30d = '缴费' |
| 转账偏好用户 | WHERE tf_prefer_level = 'high' OR primary_trx_scene_r30d = '转账' |
| 交通支付偏好 | WHERE tra_prefer_level = 'high' OR primary_trx_scene_r30d = '交通' |
| 周末交易偏好 | WHERE is_weekend_trx_prefer = '1' |
| 高退款用户 | WHERE refund_ratio_r30d > 0.1 |
| 喜欢用券用户 | WHERE coupon_usage_ratio_r30d > 0.5 |


### 5.7 活跃度
| 用户说的 | SQL 写法 |
| --- | --- |
| 活跃用户（近7天） | WHERE is_7d_active = '1' OR active_freq_level_r7d = 'high' |
| 活跃用户（近30天） | WHERE is_30d_active = '1' OR active_freq_level_r30d = 'high' |
| 沉默用户（7天未活跃） | WHERE last_active_days BETWEEN 7 AND 30 |
| 沉默用户（30天未活跃） | WHERE last_active_days > 30 |
| 流失用户（90天未活跃） | WHERE last_active_days > 90 |
| 连续活跃用户 | WHERE continuous_active_days >= 7 |
| push点击用户 | WHERE is_push_click_user = '1' OR push_click_cnt_r30d > 0 |


---

## 六、核心字段速查
### 6.1 adm_asap_base_user_label_dd（用户基础画像）
| 字段名 | 类型 | 描述 | 值域/示例 |
| --- | --- | --- | --- |
| user_id | string | 用户ID | - |
| user_status | string | 用户状态 | 'T':正常, 'Q':快速注册, 'C':注销, 'B':冻结 |
| user_age | int | 用户年龄 | -1:无年龄, >0:正常年龄 |
| user_age_group | string | 用户年龄分级 | '0':未知, '1':18岁以下, '2':18-21, '3':22-25, '4':26-30, '5':31-35, '6':36-40, '7':41-50, '8':51-60, '9':60以上 |
| user_gender | string | 性别 | 'F':女, 'M':男 |
| is_hk_drifter | string | 是否港漂 | 'CX':非永久居民, 'AX':永久居民 |
| is_ph_maid_flag | string | 是否菲佣 | '1':是, '0':否 |
| new_user_level | string | 新用户认证等级 | 'verified', 'unverified', 'pre-existing' |
| kyc_level | string | KYC等级 | 'CDD0', 'CDD1', 'CDD2', 'EKYC', 'UNKNOWN' |
| is_kyc_flag | string | 是否KYC | '1':是, '0':否 |
| life_cycle | string | 用户生命周期 | '1':新手期, '2':成长期, '3':成熟期, '4':衰退期, '5':沉默期, '6':流失期 |
| user_value | string | 用户价值 | '1' 开头为高价值 |
| register_number | string | 注册号码地区 | '86':内地, '852':香港, '853':澳门 |
| pf_language | string | 语言设置 | 'en_US', 'zh_HK', 'zh_Hans' |
| u_os | string | 操作系统 | 'ANDROID', 'IOS' |
| active_region_r30d | string | 近30天活跃区域 | 內地/香港/日本/澳門/泰國/菲律賓... |
| is_lbs_hk | string | 是否LBS香港 | '1':是, '0':否 |
| is_lbs_cn | string | 是否LBS内地 | '1':是, '0':否 |
| is_pay_qr | string | 是否收钱码用户 | '1':是, '0':否 |
| is_promo_black_flag | string | 营销黑名单 | '1':是（需排除）, '0':否 |
| is_black_list | string | 风控营销黑名单 | '1':是（需排除）, '0':否 |
| dt | string | 分区日期 | yyyyMMdd |


### 6.2 adm_asap_algo_user_label_dd（用户行为偏好）
| 字段名 | 描述 | 值域 |
| --- | --- | --- |
| pts_prefer_level | 积分权益偏好 | 'high', 'medium', 'low' |
| rp_prefer_level | 红包权益偏好 | 'high', 'medium', 'low' |
| cou_prefer_level | 优惠领券偏好 | 'high', 'medium', 'low' |
| banner_prefer_level | 首页腰封Banner偏好 | 'high', 'medium', 'low' |
| feeds_prefer_level | 首页feeds偏好 | 'high', 'medium', 'low' |
| ol_prefer_level | 线上偏好 | 'high', 'medium', 'low' |
| ll_prefer_level | 本地线下偏好 | 'high', 'medium', 'low' |
| cl_prefer_level | 跨境线下偏好 | 'high', 'medium', 'low' |
| fin01_prefer_level | 金融_EM+偏好 | 'high', 'medium', 'low' |
| em_potential_segment | eM+开通预测 | '高潜', '中潜', '低潜' |
| em_value_user | eM+用户价值 | '1':高价值, '2':中价值, '3':低价值 |
| em_marketing_sensitivity | eM+营销敏感度 | '高营销敏感度', '低营销敏感度' |
| fund_potential_segment | 基金开通预测 | '高潜', '中潜', '低潜' |
| reactivation_level | 用户回流潜力 | 'high', 'medium', 'low' |
| silence_risk_level | 用户沉默预警 | 'high', 'medium', 'low' |
| freq_uplift_level | 用户提频潜力 | 'high', 'medium', 'low' |
| dt | 分区日期 | yyyyMMdd |


### 6.3 adm_asap_pay_user_label_dd（用户交易行为）
| 字段名 | 描述 | 类型 |
| --- | --- | --- |
| trx_freq_level_r7d / r30d | 交易频次等级 | 'high', 'medium', 'low' |
| trx_amt_level_r7d / r30d | 交易金额等级 | 'high', 'medium', 'low' |
| avg_trx_amt_r7d / r30d | 笔均交易金额 | decimal |
| primary_trx_scene_r30d | 近30天主交易场景 | 线上/本地线下/跨境线下/缴费/转账... |
| primary_trx_hour_r7d | 近7天主交易时段 | 'morning', 'noon', 'afternoon', 'evening', 'night' |
| is_weekend_trx_prefer | 是否偏好周末交易 | '1':是, '0':否 |
| primary_pay_channel_r7d | 近7天主支付渠道 | 余额/银行卡/信用卡... |
| refund_cnt_r7d / r30d | 退款笔数 | int |
| refund_ratio_r30d | 近30天退款率 | decimal |
| coupon_usage_cnt_r30d | 近30天用券笔数 | int |
| coupon_usage_ratio_r30d | 近30天用券率 | decimal |
| dt | 分区日期 | yyyyMMdd |


### 6.4 adm_asap_other_action_user_label_dd（用户非交易行为）
| 字段名 | 描述 | 类型 |
| --- | --- | --- |
| active_freq_level_r7d / r30d | 活跃频次等级 | 'high', 'medium', 'low' |
| last_active_days | 距今未活跃天数 | int |
| is_7d_active | 近7天是否活跃 | '1':是, '0':否 |
| is_30d_active | 近30天是否活跃 | '1':是, '0':否 |
| continuous_active_days | 连续活跃天数 | int |
| login_cnt_r7d / r30d | 登录次数 | int |
| scan_cnt_r7d / r30d | 扫码次数 | int |
| page_view_cnt_r7d / r30d | 页面浏览次数 | int |
| banner_click_cnt_r7d | 近7天Banner点击次数 | int |
| feeds_click_cnt_r7d | 近7天feeds点击次数 | int |
| search_cnt_r7d / r30d | 搜索次数 | int |
| push_click_cnt_r7d / r30d | push点击次数 | int |
| is_push_click_user | 是否点击过push | '1':是, '0':否 |
| dt | 分区日期 | yyyyMMdd |


---

## 七、常用查询场景 SQL 示例
### 7.1 查询高价值用户画像分布（单表 base）
```sql
-- 查询维度（年龄/性别/港漂）均在 base 表，直接单表查
SELECT
    user_age_group,
    user_gender,
    is_hk_drifter,
    COUNT(DISTINCT user_id) AS user_cnt
FROM antsg_asap.adm_asap_base_user_label_dd
WHERE dt = '${bizdate}'
  AND user_value LIKE '1%'
  AND is_promo_black_flag = '0'
GROUP BY user_age_group, user_gender, is_hk_drifter
ORDER BY user_cnt DESC
```

### 7.2 查询eM+各潜力等级用户数（单表 algo）
```sql
-- eM+ 相关字段全在 algo 表，直接单表统计，无需关联 base
SELECT
    em_potential_segment,
    COUNT(DISTINCT user_id) AS user_cnt
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
GROUP BY em_potential_segment
ORDER BY user_cnt DESC
```

### 7.3 查询各交易场景用户数及笔均金额（单表 pay）
```sql
-- 交易维度全在 pay 表，直接单表统计
SELECT
    primary_trx_scene_r30d,
    COUNT(DISTINCT user_id) AS user_cnt,
    AVG(avg_trx_amt_r30d) AS avg_trx_amt
FROM antsg_asap.adm_asap_pay_user_label_dd
WHERE dt = '${bizdate}'
GROUP BY primary_trx_scene_r30d
ORDER BY user_cnt DESC
```

### 7.4 查询沉默用户的回流潜力分布（需 JOIN）
```sql
-- 沉默条件在 other_action，回流潜力字段在 algo，跨表才需要 JOIN
SELECT
    b.reactivation_level,
    COUNT(DISTINCT a.user_id) AS user_cnt,
    AVG(a.last_active_days) AS avg_silent_days
FROM (
    -- other_action：过滤日期 + 沉默用户
    SELECT user_id, last_active_days
    FROM antsg_asap.adm_asap_other_action_user_label_dd
    WHERE dt = '${bizdate}'
      AND last_active_days > 30
) a
JOIN (
    -- algo：过滤日期
    SELECT user_id, reactivation_level
    FROM anthk_sg.adm_asap_algo_user_label_dd
    WHERE dt = '${bizdate}'
) b ON a.user_id = b.user_id
GROUP BY b.reactivation_level
ORDER BY user_cnt DESC
```

### 7.5 查询eM+高潜用户的年龄性别分布（需 JOIN）
```sql
-- eM+高潜 在 algo，年龄/性别 在 base，跨表才 JOIN
SELECT
    a.user_age_group,
    a.user_gender,
    COUNT(DISTINCT a.user_id) AS em_potential_cnt
FROM (
    -- base：过滤日期
    SELECT user_id, user_age_group, user_gender
    FROM antsg_asap.adm_asap_base_user_label_dd
    WHERE dt = '${bizdate}'
) a
JOIN (
    -- algo：过滤日期 + eM+高潜
    SELECT user_id
    FROM anthk_sg.adm_asap_algo_user_label_dd
    WHERE dt = '${bizdate}'
      AND em_potential_segment = '高潜'
) b ON a.user_id = b.user_id
GROUP BY a.user_age_group, a.user_gender
```

---

## 八、查询注意事项
1. **分区字段必填**：所有表均为 `dt` 分区，格式 `yyyyMMdd`，查询时必须指定
2. **优先单表**：查询维度在哪张表就直接用那张表，无需强制关联其他表
3. **多表 JOIN 必须先过滤**：确认跨表字段需要 JOIN 时，各子查询内先 `WHERE dt + 业务条件` 再 JOIN，避免全表扫描
4. **用户去重**：用户数统计使用 `COUNT(DISTINCT user_id)`
5. **黑名单过滤**：营销场景需加 `AND is_promo_black_flag = '0' AND is_black_list = '0'`（字段在 base 表）
6. **偏好等级通用**：所有 `*_prefer_level` 字段值域均为 `'high'`, `'medium'`, `'low'`
7. **时间窗口选择**：交易/活跃类指标有 r7d（近7天）和 r30d（近30天）两种，根据需求选择
8. **潜客rank字段**：所有 `*_rank` 字段数值越小排名越高（rank=1 为最高优先级）
