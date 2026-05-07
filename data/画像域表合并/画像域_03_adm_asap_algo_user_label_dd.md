# adm_asap_algo_user_label_dd
## 一、表信息
| 项目 | 内容 |
| --- | --- |
| 表名 | adm_asap_algo_user_label_dd |
| 库名 | anthk_sg |
| 完整路径 | anthk_sg.adm_asap_algo_user_label_dd |
| 表类型 | ADM 汇总表 |
| 数据更新频率 | 日更新（T+1） |
| 分区字段 | dt（格式：yyyyMMdd） |
| 数据生命周期 | 365天 |


## 二、表描述
用户行为偏好表，包含用户的各类偏好等级、潜客分层、回流潜力、沉默预警等算法标签。该表通过机器学习模型对用户行为进行分析和预测，为精准营销、用户运营提供数据支持。主要包含权益偏好、展位偏好、业务偏好、品类偏好、eM+潜客、基金潜客、回流沉默预警等多个维度的标签。

## 三、字段列表
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| user_id | 用户ID | STRING | 用户唯一标识 |
| pts_prefer_level | 积分权益偏好等级 | STRING | 积分权益偏好等级('high':高、'medium':中、'low':低) |
| ec_prefer_level | 兑换类凭证权益偏好等级 | STRING | 兑换类凭证权益偏好等级('high':高、'medium':中、'low':低) |
| mev_prefer_level | 商户兑换券权益偏好等级 | STRING | 商户兑换券权益偏好等级('high':高、'medium':中、'low':低) |
| rp_prefer_level | 红包权益偏好等级 | STRING | 红包权益偏好等级('high':高、'medium':中、'low':低) |
| if_prefer_level | 鼓励金权益偏好等级 | STRING | 鼓励金权益偏好等级('high':高、'medium':中、'low':低) |
| faid_prefer_level | 满立减权益偏好等级 | STRING | 满立减权益偏好等级('high':高、'medium':中、'low':低) |
| banner_prefer_level | 首页腰封Banner偏好等级/腰封点击偏好 | STRING | 首页腰封Banner偏好等级('high':高、'medium':中、'low':低) |
| pay_success_prefer_level | 支付成功页偏好等级 | STRING | 支付成功页偏好等级('high':高、'medium':中、'low':低) |
| feeds_prefer_level | 首页feeds偏好等级 | STRING | 首页feeds偏好等级('high':高、'medium':中、'low':低) |
| voucher_prefer_level | 首页優惠卡片偏好等级 | STRING | 首页優惠卡片偏好等级('high':高、'medium':中、'low':低) |
| finance_prefer_level | 首頁金融卡片偏好等级 | STRING | 首頁金融卡片偏好等级('high':高、'medium':中、'low':低) |
| target_prefer_level | 首頁定投卡片偏好等级 | STRING | 首頁定投卡片偏好等级('high':高、'medium':中、'low':低) |
| ol_prefer_level | 線上偏好等级 | STRING | 線上偏好等级('high':高、'medium':中、'low':低) |
| ll_prefer_level | 本地線下偏好等级 | STRING | 本地線下偏好等级('high':高、'medium':中、'low':低) |
| cl_prefer_level | 跨境線下偏好等级 | STRING | 跨境線下偏好等级('high':高、'medium':中、'low':低) |
| pt_prefer_level | 繳費偏好等级 | STRING | 繳費偏好等级('high':高、'medium':中、'low':低) |
| tf_prefer_level | 轉賬偏好等级 | STRING | 轉賬偏好等级('high':高、'medium':中、'low':低) |
| tra_prefer_level | 交通偏好等级 | STRING | 交通偏好等级('high':高、'medium':中、'low':低) |
| rm_prefer_level | 汇款偏好等级 | STRING | 汇款偏好等级('high':高、'medium':中、'low':低) |
| sv_prefer_level | 賣券偏好等级 | STRING | 賣券偏好等级('high':高、'medium':中、'low':低) |
| fin01_prefer_level | 金融_EM+偏好等级 | STRING | 金融_EM+偏好等级('high':高、'medium':中、'low':低) |
| fin02_prefer_level | 金融_非EM+偏好等级 | STRING | 金融_非EM+偏好等级('high':高、'medium':中、'low':低) |
| cou_prefer_level | 優惠領券偏好等级 | STRING | 優惠領券偏好等级('high':高、'medium':中、'low':低) |
| ui_prefer_level | 使用積分偏好等级 | STRING | 使用積分偏好等级('high':高、'medium':中、'low':低) |
| healthcare_prefer_level | 醫療健康偏好等级 | STRING | 醫療健康偏好等级('high':高、'medium':中、'low':低) |
| fb_prefer_level | 餐飲偏好等级 | STRING | 餐飲偏好等级('high':高、'medium':中、'low':低) |
| retail_prefer_level | 零售偏好等级 | STRING | 零售偏好等级('high':高、'medium':中、'low':低) |
| travel_prefer_level | 旅遊出行偏好等级 | STRING | 旅遊出行偏好等级('high':高、'medium':中、'low':低) |
| comprehfinance_prefer_level | 綜合金融偏好等级 | STRING | 綜合金融偏好等级('high':高、'medium':中、'low':低) |
| other_prefer_level | 其他偏好等级 | STRING | 其他偏好等级('high':高、'medium':中、'low':低) |
| game_prefer_level | 遊戲偏好等级 | STRING | 遊戲偏好等级('high':高、'medium':中、'low':低) |
| recreation_prefer_level | 休閒娛樂偏好等级 | STRING | 休閒娛樂偏好等级('high':高、'medium':中、'low':低) |
| bathinghealth_prefer_level | 洗浴養身偏好等级 | STRING | 洗浴養身偏好等级('high':高、'medium':中、'low':低) |
| housekeeping_prefer_level | 家政/維修/回收偏好等级 | STRING | 家政/維修/回收偏好等级('high':高、'medium':中、'low':低) |
| filmshowsport_prefer_level | 電影/演出/體育賽事偏好等级 | STRING | 電影/演出/體育賽事偏好等级('high':高、'medium':中、'low':低) |
| beauty_prefer_level | 麗人偏好等级 | STRING | 麗人偏好等级('high':高、'medium':中、'low':低) |
| audiovisualmember_prefer_level | 影音會員偏好等级 | STRING | 影音會員偏好等级('high':高、'medium':中、'low':低) |
| telfee_prefer_level | 電訊繳費偏好等级 | STRING | 電訊繳費偏好等级('high':高、'medium':中、'low':低) |
| callcar_prefer_level | 打車偏好等级 | STRING | 打車偏好等级('high':高、'medium':中、'low':低) |
| travelservice_prefer_level | 旅行服務偏好等级 | STRING | 旅行服務偏好等级('high':高、'medium':中、'low':低) |
| tram_prefer_level | 電車偏好等级 | STRING | 電車偏好等级('high':高、'medium':中、'low':低) |
| wealthmanage_prefer_level | 財富管理偏好等级 | STRING | 財富管理偏好等级('high':高、'medium':中、'low':低) |
| otherfee_prefer_level | 其他繳費偏好等级 | STRING | 其他繳費偏好等级('high':高、'medium':中、'low':低) |
| bus_prefer_level | 巴士偏好等级 | STRING | 巴士偏好等级('high':高、'medium':中、'low':低) |
| bank_prefer_level | 銀行偏好等级 | STRING | 銀行偏好等级('high':高、'medium':中、'low':低) |
| service_prefer_level | 服務偏好等级 | STRING | 服務偏好等级('high':高、'medium':中、'low':低) |
| ferry_prefer_level | 輪渡偏好等级 | STRING | 輪渡偏好等级('high':高、'medium':中、'low':低) |
| prenatalcare_prefer_level | 產前產後護理偏好等级 | STRING | 產前產後護理偏好等级('high':高、'medium':中、'low':低) |
| govbill_prefer_level | 政府帳單偏好等级 | STRING | 政府帳單偏好等级('high':高、'medium':中、'low':低) |
| livingfee_prefer_level | 生活繳費偏好等级 | STRING | 生活繳費偏好等级('high':高、'medium':中、'low':低) |
| highspeedrail_prefer_level | 高鐵偏好等级 | STRING | 高鐵偏好等级('high':高、'medium':中、'low':低) |
| sharedservice_prefer_level | 共享服務偏好等级 | STRING | 共享服務偏好等级('high':高、'medium':中、'low':低) |
| minibus_prefer_level | 小巴偏好等级 | STRING | 小巴偏好等级('high':高、'medium':中、'low':低) |
| metro_prefer_level | 地鐵偏好等级 | STRING | 地鐵偏好等级('high':高、'medium':中、'low':低) |
| cloth_prefer_level | 服裝偏好等级 | STRING | 服裝偏好等级('high':高、'medium':中、'low':低) |
| exercise_prefer_level | 運動健身偏好等级 | STRING | 運動健身偏好等级('high':高、'medium':中、'low':低) |
| airport_prefer_level | 機場偏好等级 | STRING | 機場偏好等级('high':高、'medium':中、'low':低) |
| platformincentives_prefer_level | 平臺激勵偏好等级 | STRING | 平臺激勵偏好等级('high':高、'medium':中、'low':低) |
| userrights_prefer_level | 用戶權益偏好等级 | STRING | 用戶權益偏好等级('high':高、'medium':中、'low':低) |
| accounttransaction_prefer_level | 賬戶與交易管理偏好等级 | STRING | 賬戶與交易管理偏好等级('high':高、'medium':中、'low':低) |
| ai_brand_prefer_top_items | 用户品牌top偏好 | STRING | 用户品牌top偏好 |
| reactivation_level | 用户回流潜力等级 | STRING | 用户回流潜力等级('high':高、'medium':中、'low':低) |
| silence_risk_level | 用户沉默预警等级 | STRING | 用户沉默预警等级('high':高、'medium':中、'low':低) |
| freq_uplift_level | 用户提频潜力等级 | STRING | 用户提频潜力等级('high':高、'medium':中、'low':低) |
| prefer_level | push偏好等级/点击push偏好等级 | STRING | push偏好等级('high':高、'medium':中、'low':低) |
| r23h_prefer_level | R23h偏好等级 | STRING | R23h偏好等级('high':高、'medium':中、'low':低) |
| r22h_prefer_level | R22h偏好等级 | STRING | R22h偏好等级('high':高、'medium':中、'low':低) |
| r21h_prefer_level | R21h偏好等级 | STRING | R21h偏好等级('high':高、'medium':中、'low':低) |
| r20h_prefer_level | R20h偏好等级 | STRING | R20h偏好等级('high':高、'medium':中、'low':低) |
| r19h_prefer_level | R19h偏好等级 | STRING | R19h偏好等级('high':高、'medium':中、'low':低) |
| r18h_prefer_level | R18h偏好等级 | STRING | R18h偏好等级('high':高、'medium':中、'low':低) |
| r17h_prefer_level | R17h偏好等级 | STRING | R17h偏好等级('high':高、'medium':中、'low':低) |
| r16h_prefer_level | R16h偏好等级 | STRING | R16h偏好等级('high':高、'medium':中、'low':低) |
| r15h_prefer_level | R15h偏好等级 | STRING | R15h偏好等级('high':高、'medium':中、'low':低) |
| r14h_prefer_level | R14h偏好等级 | STRING | R14h偏好等级('high':高、'medium':中、'low':低) |
| r13h_prefer_level | R13h偏好等级 | STRING | R13h偏好等级('high':高、'medium':中、'low':低) |
| r12h_prefer_level | R12h偏好等级 | STRING | R12h偏好等级('high':高、'medium':中、'low':低) |
| r11h_prefer_level | R11h偏好等级 | STRING | R11h偏好等级('high':高、'medium':中、'low':低) |
| r10h_prefer_level | R10h偏好等级 | STRING | R10h偏好等级('high':高、'medium':中、'low':低) |
| r09h_prefer_level | R09h偏好等级 | STRING | R09h偏好等级('high':高、'medium':中、'low':低) |
| r08h_prefer_level | R08h偏好等级 | STRING | R08h偏好等级('high':高、'medium':中、'low':低) |
| r07h_prefer_level | R07h偏好等级 | STRING | R07h偏好等级('high':高、'medium':中、'low':低) |
| r06h_prefer_level | R06h偏好等级 | STRING | R06h偏好等级('high':高、'medium':中、'low':低) |
| r05h_prefer_level | R05h偏好等级 | STRING | R05h偏好等级('high':高、'medium':中、'low':低) |
| r04h_prefer_level | R04h偏好等级 | STRING | R04h偏好等级('high':高、'medium':中、'low':低) |
| r03h_prefer_level | R03h偏好等级 | STRING | R03h偏好等级('high':高、'medium':中、'low':低) |
| r02h_prefer_level | R02h偏好等级 | STRING | R02h偏好等级('high':高、'medium':中、'low':低) |
| r01h_prefer_level | R01h偏好等级 | STRING | R01h偏好等级('high':高、'medium':中、'low':低) |
| r00h_prefer_level | R00h偏好等级 | STRING | R00h偏好等级('high':高、'medium':中、'low':低) |
| em_potential_segment | eM+开通预测 | STRING | eM+开通预测(高潜、中潜、低潜) |
| em_transfer_in_label | eM+入金/存钱预测 | STRING | eM+入金预测(高入金、中入金、低入金) |
| em_value_user | eM+用户价值 | STRING | eM+用户价值('1':高价值、'2':中价值、'3':低价值) |
| em_marketing_sensitivity | eM+营销敏感度 | STRING | eM+营销敏感度（高营销敏感度,低营销敏感度） |
| em_potential_rank | eM+潜客rank | BIGINT | eM+潜客rank，数值越小，排名越高 |
| em_transfer_rank | eM+入金rank | BIGINT | eM+入金rank，数值越小，排名越高 |
| em_mkt_perfer_rank | eM+营销敏感度rank | BIGINT | eM+营销敏感度rank，数值越小，排名越高 |
| fund_potential_rank | 基金潜客rank | BIGINT | 基金潜客rank，数值越小，排名越高 |
| fund_potential_segment | 基金开通预测 | STRING | 基金开通预测（高潜、中潜、低潜） |
| em_potential_banner_score | eM+潜客分(首页Banner偏好) | BIGINT | eM+潜客分(首页Banner偏好),数值越大, eM+开通概率越高 |
| em_potential_banner_rank | eM+潜客rank(首页Banner偏好) | BIGINT | eM+潜客rank(首页Banner偏好),数值越小,排名越高 |
| fund_subs_rank | subscription rank | BIGINT | subscription rank，数值越小，认购率越高 |
| dt | 分区日期 | STRING | 分区日期，格式yyyyMMdd |


## 四、常用查询场景
### 4.1 查询高偏好用户分布
```sql
-- 查询各权益偏好的高偏好用户数
SELECT 
    pts_prefer_level,
    COUNT(DISTINCT user_id) AS user_cnt
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
  AND pts_prefer_level = 'high'
GROUP BY pts_prefer_level;
```

### 4.2 查询eM+潜客分层
```sql
-- 查询eM+各潜力等级用户数
SELECT 
    em_potential_segment,
    COUNT(DISTINCT user_id) AS user_cnt
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
GROUP BY em_potential_segment
ORDER BY user_cnt DESC;
```

### 4.3 查询基金潜客
```sql
-- 查询基金高潜用户
SELECT 
    fund_potential_segment,
    COUNT(DISTINCT user_id) AS user_cnt
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
GROUP BY fund_potential_segment
ORDER BY user_cnt DESC;
```

### 4.4 查询用户回流潜力
```sql
-- 查询各回流潜力等级用户数
SELECT 
    reactivation_level,
    COUNT(DISTINCT user_id) AS user_cnt
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
GROUP BY reactivation_level
ORDER BY user_cnt DESC;
```

### 4.5 查询沉默风险用户
```sql
-- 查询沉默风险等级分布
SELECT 
    silence_risk_level,
    COUNT(DISTINCT user_id) AS user_cnt
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
GROUP BY silence_risk_level
ORDER BY user_cnt DESC;
```

### 4.6 查询eM+高潜用户Top N
```sql
-- 查询eM+潜客排名最高的1000名用户
SELECT 
    user_id,
    em_potential_rank,
    em_potential_segment
FROM anthk_sg.adm_asap_algo_user_label_dd
WHERE dt = '${bizdate}'
  AND em_potential_segment = '高潜'
ORDER BY em_potential_rank ASC
LIMIT 1000;
```

## 五、注意事项
1. **分区字段必填**：所有查询必须指定 `dt` 分区，格式为 `yyyyMMdd`
2. **偏好等级字段通用说明**：所有 `*_prefer_level` 字段值域均为 `'high'`(高)、`'medium'`(中)、`'low'`(低)
3. **潜客分层字段说明**：
    - `em_potential_segment`: eM+开通预测（高潜、中潜、低潜）
    - `fund_potential_segment`: 基金开通预测（高潜、中潜、低潜）
    - `em_transfer_in_label`: eM+入金预测（高入金、中入金、低入金）
4. **Rank字段说明**：所有 `*_rank` 字段数值越小排名越高（rank=1 为最高优先级）
5. **eM+用户价值**：'1'表示高价值、'2'表示中价值、'3'表示低价值
6. **营销敏感度**：分为'高营销敏感度'和'低营销敏感度'
7. **时段偏好字段**：r00h-r23h 表示24小时制的各时段偏好等级
8. **关联使用**：该表需与 `adm_asap_base_user_label_dd` 通过 `user_id` + `dt` 进行关联使用
