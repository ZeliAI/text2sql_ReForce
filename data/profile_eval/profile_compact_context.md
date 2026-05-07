# 画像域 Compact Schema Context

## 全局规则
- JOIN 规则：4 张画像域表通过 user_id + dt JOIN，优先单表查询，只有跨表字段组合时才 JOIN。
- dt 规则：所有查询必须指定 dt 分区；P0 默认使用 dt = max_pt('完整表名')，除非输入明确要求固定日期。
- 用户数默认使用 COUNT(DISTINCT user_id)。

## 表与字段
### antsg_asap.adm_asap_base_user_label_dd
- 用途：用户基础画像表，包含用户的基础属性信息，如用户状态、年龄、性别、港漂标识、注册信息、认证信息、设备信息、LBS位置信息、生命周期、价值分层、风控评分等。是用户画像体系中最基础的维度表
- 字段：user_id（用户ID）、user_status（用户状态）、user_age（用户年龄）、user_gender（用户性别）、is_hk_drifter（是否港漂）、is_ph_maid_flag（是否菲佣用户）、user_birth_month（用户生日对应月份）、user_birth_day（用户生日对应日期）、user_to_birth_x_day（距离用户本年生日还有X天）、user_birth_date_gmt（认证过的出生年月日）、register_date（注册日期）、register_gmt（注册时间）、register_days（注册距今天数）、register_number（注冊號碼）、new_user_level（新用户认证等级）、is_pay_qr（是否收钱码用户）、is_taxi_merchant（是否出租车收钱码用户）、cert_cn_nation（认证通过的国籍）、user_age_group（用户年龄分级）、new_old_user_level（新老用户分级）、user_type（用户类型）、is_have_name_flag（是否有名字）、is_actived_flag（是否激活）、actived_days（用户激活到当前天数）、nationality（用户国籍）、careers（用户职业）、credential_type（用户认证证件类型）、pf_language（语言设置）、is_promo_black_flag（是否营销黑名单用户）、balance（当日钱包余额）、register_from（用户注册来源）、is_bind_mobile_flag（是否绑定手机）、is_app_739_versio（app版本号是否小于7.3.9）、u_device_model（机型）、u_device_resolution（分辨率）、u_os（操作系统）、u_resident_province（常驻省份）、u_resident_city（常驻城市）、is_push_power（用户push权限是否开启）、is_push_gw（是否接收push）、is_lang_en（最近一次登录设置的语言是英文）、is_lang_zh（最近一次登录设置的语言是中文）、is_login_ios（最近一次登录使用IOS）、is_login_android（最近一次登录使用安卓）、kyc_level（kyc认证等级）、is_kyc_flag（用户是否KYCS）、is_ekyc（是否ekycS）、life_cycle（用户生命周期）、user_value（用户价值）、user_history_value（用户历史价值）、active_region_r7d（最近7天活跃区域）、active_region_r15d（最近15天活跃区域）、active_region_r30d（最近30天活跃区域）、active_region_r365d（最近365天活跃区域）、active_region_his（历史至今的活跃区域）、is_lbs_hk（是否曾经lbs香港）、is_lbs_cn（是否曾经lbs内地）、is_lbs_ma（是否曾经lbs澳门）、is_lbs_jp（是否曾经lbs日本）、city_num_r1y（近1年出行城市数）、city_num_r2y（近2年出行城市数）、city_num_r3y（近3年出行城市数）、country_num_r1y（近1年出行国家数）、country_num_r2y（近2年出行国家数）、country_num_r3y（近3年出行国家数）、travel_days（近半年在境外的天数）、travel_days_r1y（近1年在境外的天数）、travel_days_r2y（近2年在境外的天数）、travel_days_r3y（近3年在境外的天数）、isoversea_2year（近2年是否有境外lbs）、is_black_list（是否风控的营销黑名单）、pl_apply_predict_score（钱包银行联合信贷模型 标准用户得分）、pl_apply_predict_score_ph_maid（钱包银行联合信贷模型 菲佣用户得分）、pl_apply_user_rank（钱包银行联合信贷模型 标准用户和菲佣用户合并 并转化为银行的10分制）、pl_apply_user_rank_v3（钱包银行联合信贷模型 v3版本用户得分）、ploan_riskseg（PloanA卡评级）、mcard_riskseg（M卡评级）、dt（分区日期）

### anthk_sg.adm_asap_algo_user_label_dd
- 用途：用户行为偏好表，包含用户的各类偏好等级、潜客分层、回流潜力、沉默预警等算法标签。该表通过机器学习模型对用户行为进行分析和预测，为精准营销、用户运营提供数据支持。主要包含权益偏好、展位偏好、业务偏好、品类偏好、eM+潜客、基金潜客、回流沉默预警等多个维度的标签。
- 字段：user_id（用户ID）、pts_prefer_level（积分权益偏好等级）、ec_prefer_level（兑换类凭证权益偏好等级）、mev_prefer_level（商户兑换券权益偏好等级）、rp_prefer_level（红包权益偏好等级）、if_prefer_level（鼓励金权益偏好等级）、faid_prefer_level（满立减权益偏好等级）、banner_prefer_level（首页腰封Banner偏好等级/腰封点击偏好）、pay_success_prefer_level（支付成功页偏好等级）、feeds_prefer_level（首页feeds偏好等级）、voucher_prefer_level（首页優惠卡片偏好等级）、finance_prefer_level（首頁金融卡片偏好等级）、target_prefer_level（首頁定投卡片偏好等级）、ol_prefer_level（線上偏好等级）、ll_prefer_level（本地線下偏好等级）、cl_prefer_level（跨境線下偏好等级）、pt_prefer_level（繳費偏好等级）、tf_prefer_level（轉賬偏好等级）、tra_prefer_level（交通偏好等级）、rm_prefer_level（汇款偏好等级）、sv_prefer_level（賣券偏好等级）、fin01_prefer_level（金融_EM+偏好等级）、fin02_prefer_level（金融_非EM+偏好等级）、cou_prefer_level（優惠領券偏好等级）、ui_prefer_level（使用積分偏好等级）、healthcare_prefer_level（醫療健康偏好等级）、fb_prefer_level（餐飲偏好等级）、retail_prefer_level（零售偏好等级）、travel_prefer_level（旅遊出行偏好等级）、comprehfinance_prefer_level（綜合金融偏好等级）、other_prefer_level（其他偏好等级）、game_prefer_level（遊戲偏好等级）、recreation_prefer_level（休閒娛樂偏好等级）、bathinghealth_prefer_level（洗浴養身偏好等级）、housekeeping_prefer_level（家政/維修/回收偏好等级）、filmshowsport_prefer_level（電影/演出/體育賽事偏好等级）、beauty_prefer_level（麗人偏好等级）、audiovisualmember_prefer_level（影音會員偏好等级）、telfee_prefer_level（電訊繳費偏好等级）、callcar_prefer_level（打車偏好等级）、travelservice_prefer_level（旅行服務偏好等级）、tram_prefer_level（電車偏好等级）、wealthmanage_prefer_level（財富管理偏好等级）、otherfee_prefer_level（其他繳費偏好等级）、bus_prefer_level（巴士偏好等级）、bank_prefer_level（銀行偏好等级）、service_prefer_level（服務偏好等级）、ferry_prefer_level（輪渡偏好等级）、prenatalcare_prefer_level（產前產後護理偏好等级）、govbill_prefer_level（政府帳單偏好等级）、livingfee_prefer_level（生活繳費偏好等级）、highspeedrail_prefer_level（高鐵偏好等级）、sharedservice_prefer_level（共享服務偏好等级）、minibus_prefer_level（小巴偏好等级）、metro_prefer_level（地鐵偏好等级）、cloth_prefer_level（服裝偏好等级）、exercise_prefer_level（運動健身偏好等级）、airport_prefer_level（機場偏好等级）、platformincentives_prefer_level（平臺激勵偏好等级）、userrights_prefer_level（用戶權益偏好等级）、accounttransaction_prefer_level（賬戶與交易管理偏好等级）、ai_brand_prefer_top_items（用户品牌top偏好）、reactivation_level（用户回流潜力等级）、silence_risk_level（用户沉默预警等级）、freq_uplift_level（用户提频潜力等级）、prefer_level（push偏好等级/点击push偏好等级）、r23h_prefer_level（R23h偏好等级）、r22h_prefer_level（R22h偏好等级）、r21h_prefer_level（R21h偏好等级）、r20h_prefer_level（R20h偏好等级）、r19h_prefer_level（R19h偏好等级）、r18h_prefer_level（R18h偏好等级）、r17h_prefer_level（R17h偏好等级）、r16h_prefer_level（R16h偏好等级）、r15h_prefer_level（R15h偏好等级）、r14h_prefer_level（R14h偏好等级）、r13h_prefer_level（R13h偏好等级）、r12h_prefer_level（R12h偏好等级）、r11h_prefer_level（R11h偏好等级）、r10h_prefer_level（R10h偏好等级）、r09h_prefer_level（R09h偏好等级）、r08h_prefer_level（R08h偏好等级）、r07h_prefer_level（R07h偏好等级）、r06h_prefer_level（R06h偏好等级）、r05h_prefer_level（R05h偏好等级）、r04h_prefer_level（R04h偏好等级）、r03h_prefer_level（R03h偏好等级）、r02h_prefer_level（R02h偏好等级）、r01h_prefer_level（R01h偏好等级）、r00h_prefer_level（R00h偏好等级）、em_potential_segment（eM+开通预测）、em_transfer_in_label（eM+入金/存钱预测）、em_value_user（eM+用户价值）、em_marketing_sensitivity（eM+营销敏感度）、em_potential_rank（eM+潜客rank）、em_transfer_rank（eM+入金rank）、em_mkt_perfer_rank（eM+营销敏感度rank）、fund_potential_rank（基金潜客rank）、fund_potential_segment（基金开通预测）、em_potential_banner_score（eM+潜客分(首页Banner偏好)）、em_potential_banner_rank（eM+潜客rank(首页Banner偏好)）、fund_subs_rank（subscription rank）、dt（分区日期）

### antsg_asap.adm_asap_pay_user_label_dd
- 用途：用户交易行为画像表，包含用户绑卡、支付、充值、转账、理财等交易行为标签。该表记录用户的交易习惯、支付方式偏好、出行服务使用、金融理财行为等多维度交易特征，为用户运营、精准营销、风险控制提供数据支持。
- 字段：is_bank_no（是否绑定非直连银行）、is_card_info（是否绑卡）、effective_bind_card_cnt（当前有效绑卡数）、bind_card_cnt（历史绑卡数）、is_bind_boci（当前是否绑定中银信用卡）、is_bind_credit（当前是否绑定VM或中银信用卡）、is_bank_bind（当前是否绑定银行卡）、is_bind_fps（当前是否绑定FPS）、transact_amt_r1d（最近1天内交易金额）、transact_amt_r7d（最近7天内交易金额）、transact_amt_r30d（最近30天内交易金额）、transact_num_r1d（最近1天内交易次数）、transact_num_r7d（最近7天内交易次数）、transact_num_r30d（最近30天内交易次数）、pay_level_r30d（用户近30天支付活跃分级）、local_offline_scene_cnt_r30d（最近30天交易笔数-本地線下）、online_scene_cnt_r30d（最近30天交易笔数-線上）、transfer_scene_cnt_r30d（最近30天交易笔数-轉賬）、fee_payment_scene_cnt_r30d（最近30天交易笔数-繳費）、crossborder_scene_cnt_r30d（最近30天交易笔数-跨境線下）、transport_scene_cnt_r30d（最近30天交易笔数-交通）、finance_scene_cnt_r30d（最近30天交易笔数-金融）、topup_cnt_r1d（1日充值笔数）、topup_cnt_r7d（7日内充值笔数）、topup_cnt_r30d（30日内充值笔数）、topup_amt_r1d（1日充值金额）、topup_amt_r7d（7日内充值金额）、topup_amt_r30d（30日内充值金额）、is_local_buscode（是否開通本地乘車碼）、is_cross_buscode（是否開通跨境乘車碼）、is_auth_taxi（是否授權打車）、taxi_gaode_cnt_r30d（最近30天使用高德打车次数）、taxi_didi_cnt_r30d（最近30天使用滴滴打车次数）、high_rail_r30d（最近30天乘坐高铁次数）、is_register_emplus（是否开通eM+）、emplus_balance_amt_range（eM+余额区间）、em_deposit_cnts_r30d（用户最近30天入金次数）、em_deposit_amounts_r30d（用户最近30天入金金额）、fund_holdings_amt（个人持仓总值）、cur_fund_holdings_cnt（当前持仓数量）、government_payment_r30（最近30天的政府缴费场景）、living_payment_r30（最近30天的生活缴费场景）、telecom_payment_r30（最近30天的電讯缴费场景）、trx_freq_level_r7d（交易频次等级）、trx_freq_level_r30d（交易频次等级）、trx_amt_level_r7d（交易金额等级）、trx_amt_level_r30d（交易金额等级）、avg_trx_amt_r7d（笔均交易金额）、avg_trx_amt_r30d（笔均交易金额）、primary_trx_scene_r30d（近30天主交易场景）、primary_trx_hour_r7d（近7天主交易时段）、is_weekend_trx_prefer（是否偏好周末交易）、primary_pay_channel_r7d（近7天主支付渠道）、refund_cnt_r7d（退款笔数）、refund_cnt_r30d（退款笔数）、refund_ratio_r30d（近30天退款率）、coupon_usage_cnt_r30d（近30天用券笔数）、coupon_usage_ratio_r30d（近30天用券率）、dt（分区日期）

### antsg_asap.adm_asap_other_action_user_label_dd
- 用途：用户非交易行为画像表，包含用户登录、活跃、领券、核销、关注商户等非交易行为标签。该表记录用户的非交易行为特征，包括APP访问、权益领取、商户关注、积分使用等行为，为用户运营、精准营销提供数据支持。
- 字段：user_active_r3d（最近3天活跃天数）、user_active_r7d（最近7天活跃天数）、user_active_r30d（最近30天活跃天数）、login_cnt_r1d（近1日登录次数）、login_cnt_r7d（7日内登录次数）、login_cnt_r30d（30日内登录次数）、user_activity_level（用户活跃等级）、user_login_frequency（用户登录频次）、is_7d_active（近7天是否活跃）、is_30d_active（近30天是否活跃）、send_cnt_r1d（用户最近1天领券数量）、send_cnt_r7d（用户最近7天领券数量）、send_cnt_r30d（用户最近30天领券数量）、use_cnt_r1d（用户最近1天核销券数量）、use_cnt_r7d（用户最近7天核销券数量）、use_cnt_r30d（用户最近30天核销券数量）、equity_send_cnt_pts_r7d（用户过去7天在积分权益的领取次数）、equity_use_cnt_pts_r7d（用户过去7天在积分权益的核销次数）、equity_send_cnt_rp_r7d（用户过去7天在红包权益的领取次数）、equity_use_cnt_rp_r7d（用户过去7天在红包权益的核销次数）、equity_send_cnt_pts_r30d（用户过去30天在积分权益的领取次数）、equity_use_cnt_pts_r30d（用户过去30天在积分权益的核销次数）、is_point_new_user（是否积分新用户）、is_point_growing_user（是否积分成长用户）、is_point_active_user（是否成熟积分用户）、is_point_lost_user（是否积分流失用户）、available_point_total（总积分可用数量）、user_push_exposure_pv_r30d（用户近30天push触达次数）、user_push_exposure_pv_r7d（用户近7天push触达次数）、user_push_cilck_pv_r30d（用户近30天push点击次数）、user_push_cilck_pv_r7d（用户近7天push点击次数）、user_push_activity_level（用户push活跃等级）、paper_clk_r7d（最近7天腰封点击次数）、paper_clk_r30d（最近30天腰封点击次数）、feeds_clk_r7d（最近7天feeds点击次数）、feeds_clk_r30d（最近30天feeds点击次数）、push_clk_r7d（最近7天push点击次数）、push_clk_r30d（最近30天push点击次数）、is_follow_food_effective_flag（当前是否关注餐饮商户）、is_follow_ent_effective_flag（当前是否关注休闲娱乐商户）、is_follow_trans_effective_flag（当前是否关注交通出行商户）、follow_cnt_r7d（过去7日关注商户数）、follow_cnt_r30d（过去30日关注商户数）、active_freq_level_r7d（活跃频次等级）、active_freq_level_r30d（活跃频次等级）、last_active_days（距今未活跃天数）、continuous_active_days（连续活跃天数）、scan_cnt_r7d（扫码次数）、scan_cnt_r30d（扫码次数）、page_view_cnt_r7d（页面浏览次数）、page_view_cnt_r30d（页面浏览次数）、banner_click_cnt_r7d（近7天Banner点击次数）、feeds_click_cnt_r7d（近7天feeds点击次数）、search_cnt_r7d（搜索次数）、search_cnt_r30d（搜索次数）、push_click_cnt_r7d（push点击次数）、push_click_cnt_r30d（push点击次数）、is_push_click_user（是否点击过push）、dt（分区日期）

## 常用业务术语映射
- 正常用户 -> WHERE user_status = 'T'
- 注销用户 -> WHERE user_status = 'C'
- 冻结用户 -> WHERE user_status = 'B'
- 新用户（新手期） -> WHERE life_cycle = '1'
- 活跃用户（成长期/成熟期） -> WHERE life_cycle IN ('2', '3')
- 沉默用户（沉默期） -> WHERE life_cycle = '5'
- 流失用户（流失期） -> WHERE life_cycle IN ('6', '61')
- 高价值用户 -> WHERE user_value LIKE '1%' OR user_history_value = '高'
- 低价值用户 -> WHERE user_value LIKE '8%' OR user_history_value = '低'
- 港漂用户 -> WHERE is_hk_drifter = 'CX'
- 本地用户（永久居民） -> WHERE is_hk_drifter = 'AX'
- 菲佣用户 -> WHERE is_ph_maid_flag = '1'
- 已认证用户 -> WHERE new_user_level = 'verified' OR is_kyc_flag = '1'
- 未认证用户 -> WHERE new_user_level = 'unverified'
- 商户用户（收钱码） -> WHERE is_pay_qr = '1'
- 营销黑名单（需排除） -> WHERE is_promo_black_flag = '0' AND is_black_list = '0'
- iOS用户 -> WHERE u_os = 'IOS' OR is_login_ios = '1'
- 安卓用户 -> WHERE u_os = 'ANDROID' OR is_login_android = '1'
- 英文偏好用户 -> WHERE pf_language = 'en_US' OR is_lang_en = '1'
- 中文偏好用户 -> WHERE pf_language IN ('zh_HK', 'zh_Hans') OR is_lang_zh = '1'
- 内地用户 -> WHERE register_number = '86' OR active_region_r30d = '內地' OR is_lbs_cn = '1'
- 香港用户 -> WHERE register_number = '852' OR active_region_r30d = '香港' OR is_lbs_hk = '1'
- 澳门用户 -> WHERE register_number = '853'
- 18岁以下 -> WHERE user_age_group = '1' OR user_age < 18
- 18-25岁 -> WHERE user_age_group IN ('2', '3') OR (user_age >= 18 AND user_age <= 25)
- 26-35岁 -> WHERE user_age_group IN ('4', '5') OR (user_age >= 26 AND user_age <= 35)
- 36-50岁 -> WHERE user_age_group IN ('6', '7') OR (user_age >= 36 AND user_age <= 50)
- 50岁以上 -> WHERE user_age_group IN ('8', '9') OR user_age > 50
- 年轻用户 -> WHERE user_age_group IN ('1', '2', '3', '4')
- 中年用户 -> WHERE user_age_group IN ('5', '6', '7')
- 老年用户 -> WHERE user_age_group IN ('8', '9')
- 高偏好 -> WHERE xxx_prefer_level = 'high'
- 中偏好 -> WHERE xxx_prefer_level = 'medium'
- 低偏好 -> WHERE xxx_prefer_level = 'low'
- 偏好某业务 -> WHERE xxx_prefer_level IN ('high', 'medium')
- eM+高潜用户 -> WHERE em_potential_segment = '高潜'
- eM+中潜用户 -> WHERE em_potential_segment = '中潜'
- eM+高价值用户 -> WHERE em_value_user = '1'
- eM+营销敏感用户 -> WHERE em_marketing_sensitivity = '高营销敏感度'
- 基金高潜用户 -> WHERE fund_potential_segment = '高潜'
- 回流潜力高用户 -> WHERE reactivation_level = 'high'
- 沉默风险高用户 -> WHERE silence_risk_level = 'high'
- 提频潜力高用户 -> WHERE freq_uplift_level = 'high'
- 高频交易用户 -> WHERE trx_freq_level_r30d = 'high'
- 高消费用户 -> WHERE trx_amt_level_r30d = 'high'
- 线上支付偏好 -> WHERE primary_trx_scene_r30d = '线上' OR ol_prefer_level = 'high'
- 线下支付偏好 -> WHERE primary_trx_scene_r30d = '本地线下' OR ll_prefer_level = 'high'
- 跨境支付偏好 -> WHERE primary_trx_scene_r30d = '跨境线下' OR cl_prefer_level = 'high'
- 缴费偏好用户 -> WHERE pt_prefer_level = 'high' OR primary_trx_scene_r30d = '缴费'
- 转账偏好用户 -> WHERE tf_prefer_level = 'high' OR primary_trx_scene_r30d = '转账'
- 交通支付偏好 -> WHERE tra_prefer_level = 'high' OR primary_trx_scene_r30d = '交通'
- 周末交易偏好 -> WHERE is_weekend_trx_prefer = '1'
- 高退款用户 -> WHERE refund_ratio_r30d > 0.1
- 喜欢用券用户 -> WHERE coupon_usage_ratio_r30d > 0.5
- 活跃用户（近7天） -> WHERE is_7d_active = '1' OR active_freq_level_r7d = 'high'
- 活跃用户（近30天） -> WHERE is_30d_active = '1' OR active_freq_level_r30d = 'high'
- 沉默用户（7天未活跃） -> WHERE last_active_days BETWEEN 7 AND 30
- 沉默用户（30天未活跃） -> WHERE last_active_days > 30
- 流失用户（90天未活跃） -> WHERE last_active_days > 90
- 连续活跃用户 -> WHERE continuous_active_days >= 7
- push点击用户 -> WHERE is_push_click_user = '1' OR push_click_cnt_r30d > 0

## 指标口径
- 用户数：COUNT(DISTINCT user_id)；去重用户数
- 年龄平均值：AVG(user_age) WHERE user_age > 0；排除 -1（无年龄）的用户
- 港漂占比：COUNT(CASE WHEN is_hk_drifter = 'CX' THEN 1 END) / NULLIF(COUNT(*), 0)；CX = 非永久居民
- 女性占比：COUNT(CASE WHEN user_gender = 'F' THEN 1 END) / NULLIF(COUNT(*), 0)；-
- 认证率：COUNT(CASE WHEN new_user_level = 'verified' THEN 1 END) / NULLIF(COUNT(*), 0)；-
- KYC率：COUNT(CASE WHEN is_kyc_flag = '1' THEN 1 END) / NULLIF(COUNT(*), 0)；-
- 高价值用户数：COUNT(CASE WHEN user_value LIKE '1%' THEN 1 END)；user_value '1' 开头为高价值
- 新用户数（新手期）：COUNT(CASE WHEN life_cycle = '1' THEN 1 END)；-
- 沉默用户数：COUNT(CASE WHEN life_cycle = '5' THEN 1 END)；-
- 流失用户数：COUNT(CASE WHEN life_cycle IN ('6', '61') THEN 1 END)；-
- 高积分偏好用户数：COUNT(CASE WHEN pts_prefer_level = 'high' THEN 1 END)
- 腰封高偏好用户占比：COUNT(CASE WHEN banner_prefer_level = 'high' THEN 1 END) / NULLIF(COUNT(*), 0)
- eM+高潜用户数：COUNT(CASE WHEN em_potential_segment = '高潜' THEN 1 END)
- eM+高价值用户数：COUNT(CASE WHEN em_value_user = '1' THEN 1 END)
- 基金高潜用户数：COUNT(CASE WHEN fund_potential_segment = '高潜' THEN 1 END)
- 线上高偏好用户数：COUNT(CASE WHEN ol_prefer_level = 'high' THEN 1 END)
- 回流高潜用户数：COUNT(CASE WHEN reactivation_level = 'high' THEN 1 END)
- 沉默风险高用户数：COUNT(CASE WHEN silence_risk_level = 'high' THEN 1 END)
- 高频交易用户数：COUNT(CASE WHEN trx_freq_level_r30d = 'high' THEN 1 END)
- 高消费用户数：COUNT(CASE WHEN trx_amt_level_r30d = 'high' THEN 1 END)
- 平均近30天交易笔均金额：AVG(avg_trx_amt_r30d)
- 退款率（平均）：AVG(refund_ratio_r30d)
- 用券率（平均）：AVG(coupon_usage_ratio_r30d)
- 线上交易偏好用户占比：COUNT(CASE WHEN primary_trx_scene_r30d = '线上' THEN 1 END) / NULLIF(COUNT(*), 0)
- 月活跃用户数：COUNT(CASE WHEN is_30d_active = '1' THEN 1 END)
- 周活跃用户数：COUNT(CASE WHEN is_7d_active = '1' THEN 1 END)
- 沉默用户数（30天未活跃）：COUNT(CASE WHEN last_active_days > 30 THEN 1 END)
- 高活跃用户占比：COUNT(CASE WHEN active_freq_level_r30d = 'high' THEN 1 END) / NULLIF(COUNT(*), 0)
- 平均登录次数（近30天）：AVG(login_cnt_r30d)
- push点击用户数：COUNT(CASE WHEN is_push_click_user = '1' THEN 1 END)
