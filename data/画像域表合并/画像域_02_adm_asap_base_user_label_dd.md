# adm_asap_base_user_label_dd
## 一、表信息
| 项目 | 内容 |
| --- | --- |
| 表名 | adm_asap_base_user_label_dd |
| 库名 | antsg_asap |
| 完整路径 | antsg_asap.adm_asap_base_user_label_dd |
| 表类型 | ADM 汇总表 |
| 数据更新频率 | 日更新（T+1） |
| 分区字段 | dt（格式：yyyyMMdd） |
| 数据生命周期 | 365天 |


## 二、表描述
用户基础画像表，包含用户的基础属性信息，如用户状态、年龄、性别、港漂标识、注册信息、认证信息、设备信息、LBS位置信息、生命周期、价值分层、风控评分等。是用户画像体系中最基础的维度表

## 三、字段列表
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| user_id | 用户ID | STRING | 用户唯一标识 |
| user_status | 用户状态 | STRING | 用户状态（'T'：正常，'Q'：快速注册，'C'：注销，'B'：冻结） |
| user_age | 用户年龄 | BIGINT | 用户年龄（数值类型，没有年龄：-1，正常年龄取值范围 >0 ） |
| user_gender | 用户性别 | STRING | 用户性别('F':女 、'M'：男） |
| is_hk_drifter | 是否港漂 | STRING | 是否港漂（'CX'：非永久居民，'AX'：永久居民） |
| is_ph_maid_flag | 是否菲佣用户 | STRING | 是否菲佣用户('1':是、'0:'否) |
| user_birth_month | 用户生日对应月份 | STRING | 用户生日对应月份(01-12),未认证是空(null) |
| user_birth_day | 用户生日对应日期 | STRING | 用户生日对应日期(01-31),未认证是空(null) |
| user_to_birth_x_day | 距离用户本年生日还有X天 | STRING | 距离用户本年生日还有X天,未认证是空(null),本年生日已过为(-1) |
| user_birth_date_gmt | 认证过的出生年月日 | STRING | 认证过的出生年月日,未认证是空(null) |
| register_date | 注册日期 | STRING | 注册日期cn(到天) |
| register_gmt | 注册时间 | STRING | 注册时间cn(到秒() |
| register_days | 注册距今天数 | BIGINT | 注册距今天数 默认-1 |
| register_number | 注冊號碼 | STRING | 注冊號碼（'86'、'852'、'853'、'其他'） |
| new_user_level | 新用户认证等级 | STRING | 新用户认证等级('verified','unverified','pre-existing') |
| is_pay_qr | 是否收钱码用户 | STRING | 是否收钱码用户('1':是、'0:'否) |
| is_taxi_merchant | 是否出租车收钱码用户 | STRING | 是否出租车收钱码用户('1':是、'0:'否) |
| cert_cn_nation | 认证通过的国籍 | STRING | 认证通过的国籍(中文)('未认证'、'越南'、'日本'、'菲律宾'、'泰国'、'韩国'、'香港'、'印度尼西亚'、'中国内地'、'其他国家/地区') |
| user_age_group | 用户年龄分级 | STRING | 用户年龄分级（'0':未知、'1':18岁以下、'2':18岁到21岁、'3':22岁到25岁、'4':26岁到30岁、'5':31岁到35岁、'6':36岁到40岁、'7':41岁到50岁、'8':51岁到60岁、'9':60岁以上） |
| new_old_user_level | 新老用户分级 | STRING | 新老用户分级（'1':未活跃、'2':7日内首活、'3':30日内首活、4:365日内首活、5:365日前首活） |
| user_type | 用户类型 | STRING | 用户类型 ('1'：公司，'2'：个人) |
| is_have_name_flag | 是否有名字 | STRING | 是否有名字('1':是、'0:'否) |
| is_actived_flag | 是否激活 | STRING | 是否激活('1':是、'0:'否) |
| actived_days | 用户激活到当前天数 | BIGINT | 用户激活到当前天数 |
| nationality | 用户国籍 | STRING | 用户国籍 |
| careers | 用户职业 | STRING | 用户职业 |
| credential_type | 用户认证证件类型 | STRING | 用户认证证件类型 |
| pf_language | 语言设置 | STRING | 语言设置('en_US'、'zh_HK'、'zh_Hans'、'other_language') |
| is_promo_black_flag | 是否营销黑名单用户 | STRING | 是否营销黑名单用户('1':是、'0:'否) |
| balance | 当日钱包余额 | BIGINT | 当日钱包余额 |
| register_from | 用户注册来源 | STRING | 用户注册来源 |
| is_bind_mobile_flag | 是否绑定手机 | STRING | 是否绑定手机 ('1':是、'0:'否) |
| is_app_739_versio | app版本号是否小于7.3.9 | STRING | app版本号是否小于7.3.9('1':是、'0:'否) |
| u_device_model | 机型 | STRING | 机型_流量日志 |
| u_device_resolution | 分辨率 | STRING | 分辨率，如: 412*883_流量日志 |
| u_os | 操作系统 | STRING | 操作系统: ANDROID/IOS_流量日志（ 'ANDROID'、'IOS'） |
| u_resident_province | 常驻省份 | STRING | 常驻省份_流量日志 |
| u_resident_city | 常驻城市 | STRING | 常驻城市_流量日志 |
| is_push_power | 用户push权限是否开启 | STRING | 用户push权限是否开启('1':是、'0:'否) |
| is_push_gw | 是否接收push | STRING | 是否接收push('1':是、'0:'否) |
| is_lang_en | 最近一次登录设置的语言是英文 | STRING | 最近一次登录设置的语言是英文('1':是、'0:'否) |
| is_lang_zh | 最近一次登录设置的语言是中文 | STRING | 最近一次登录设置的语言是中文('1':是、'0:'否) |
| is_login_ios | 最近一次登录使用IOS | STRING | 最近一次登录使用IOS('1':是、'0:'否) |
| is_login_android | 最近一次登录使用安卓 | STRING | 最近一次登录使用安卓('1':是、'0:'否) |
| kyc_level | kyc认证等级 | STRING | kyc认证等级('CDD1'、'CDD2'、'EKYC'、'UNKNOWN_KYC_LEVEL'、'CDD0') |
| is_kyc_flag | 用户是否KYCS | STRING | 用户是否KYCS('1':是、'0:'否) |
| is_ekyc | 是否ekycS | STRING | 是否ekycS('1':是、'0:'否) |
| life_cycle | 用户生命周期 | STRING | 用户生命周期 ('1':新手期用户、'2':成长期用户、'3':成熟期用户、'4':衰退期用户、'5':沉默期用户、'6':流失期用户、'61':流失期用户_非AAU) |
| user_value | 用户价值 | STRING | 用户价值('1'：高价值用户_AAU、'2'：一般价值用户_AAU、'3'：重点发展用户_AAU、'4'：一般发展用户_AAU、'5'：重点保持用户_AAU、'51'：重点保持用户_非AAU、'6'：一般保持用户_AAU、'61'：一般保持用户_非AAU、'7'：重点挽留用户_AAU、'71'：重点挽留用户_非AAU、'8'：低价值用户_AAU、'81'：低价值用户_非AAU) |
| user_history_value | 用户历史价值 | STRING | 用户历史价值(高、中、低) |
| active_region_r7d | 最近7天活跃区域 | STRING | 最近7天活跃区域:(內地,香港,日本,澳門,泰國,菲律賓,臺灣,韓國,英國,馬來西亞,新加坡,越南,印度尼西亞,緬甸,柬埔寨,其它),默认值null |
| active_region_r15d | 最近15天活跃区域 | STRING | 最近15天活跃区域:(內地,香港,日本,澳門,泰國,菲律賓,臺灣,韓國,英國,馬來西亞,新加坡,越南,印度尼西亞,緬甸,柬埔寨,其它),默认值null |
| active_region_r30d | 最近30天活跃区域 | STRING | 最近30天活跃区域:(內地,香港,日本,澳門,泰國,菲律賓,臺灣,韓國,英國,馬來西亞,新加坡,越南,印度尼西亞,緬甸,柬埔寨,其它),默认值null |
| active_region_r365d | 最近365天活跃区域 | STRING | 最近365天活跃区域:(內地,香港,日本,澳門,泰國,菲律賓,臺灣,韓國,英國,馬來西亞,新加坡,越南,印度尼西亞,緬甸,柬埔寨,其它),默认值null |
| active_region_his | 历史至今的活跃区域 | STRING | 历史至今的活跃区域:(內地,香港,日本,澳門,泰國,菲律賓,臺灣,韓國,英國,馬來西亞,新加坡,越南,印度尼西亞,緬甸,柬埔寨,其它),默认值null |
| is_lbs_hk | 是否曾经lbs香港 | STRING | 是否曾经lbs香港('1':是、'0:'否) |
| is_lbs_cn | 是否曾经lbs内地 | STRING | 是否曾经lbs内地('1':是、'0:'否) |
| is_lbs_ma | 是否曾经lbs澳门 | STRING | 是否曾经lbs澳门('1':是、'0:'否) |
| is_lbs_jp | 是否曾经lbs日本 | STRING | 是否曾经lbs日本('1':是、'0:'否) |
| city_num_r1y | 近1年出行城市数 | BIGINT | 近1年出行城市数 |
| city_num_r2y | 近2年出行城市数 | BIGINT | 近2年出行城市数 |
| city_num_r3y | 近3年出行城市数 | BIGINT | 近3年出行城市数 |
| country_num_r1y | 近1年出行国家数 | BIGINT | 近1年出行国家数 |
| country_num_r2y | 近2年出行国家数 | BIGINT | 近2年出行国家数 |
| country_num_r3y | 近3年出行国家数 | BIGINT | 近3年出行国家数 |
| travel_days | 近半年在境外的天数 | BIGINT | 近半年在境外的天数 |
| travel_days_r1y | 近1年在境外的天数 | BIGINT | 近1年在境外的天数 |
| travel_days_r2y | 近2年在境外的天数 | BIGINT | 近2年在境外的天数 |
| travel_days_r3y | 近3年在境外的天数 | BIGINT | 近3年在境外的天数 |
| isoversea_2year | 近2年是否有境外lbs | STRING | 近2年是否有境外lbs('1':是、'0:'否) |
| is_black_list | 是否风控的营销黑名单 | STRING | 是否风控的营销黑名单T+2更新('1':是、'0:'否) |
| pl_apply_predict_score | 钱包银行联合信贷模型 标准用户得分 | BIGINT | 钱包银行联合信贷模型 标准用户得分 默认9999 |
| pl_apply_predict_score_ph_maid | 钱包银行联合信贷模型 菲佣用户得分 | BIGINT | 钱包银行联合信贷模型 菲佣用户得分 默认9999 |
| pl_apply_user_rank | 钱包银行联合信贷模型 标准用户和菲佣用户合并 并转化为银行的10分制 | BIGINT | 钱包银行联合信贷模型 标准用户和菲佣用户合并 并转化为银行的10分制 无得分为9999 |
| pl_apply_user_rank_v3 | 钱包银行联合信贷模型 v3版本用户得分 | BIGINT | 钱包银行联合信贷模型 v3版本用户得分 范围0-9 默认9999 |
| ploan_riskseg | PloanA卡评级 | BIGINT | PloanA卡评级 范围0-9 默认999 |
| mcard_riskseg | M卡评级 | BIGINT | M卡评级 范围0-9 默认999 |
| dt | 分区日期 | STRING | 分区日期，格式yyyyMMdd |


## 四、常用查询场景
### 4.1 查询用户基础属性分布
```sql
-- 查询各年龄段用户分布
SELECT 
    user_age_group,
    COUNT(DISTINCT user_id) AS user_cnt
FROM antsg_asap.adm_asap_base_user_label_dd
WHERE dt = '${bizdate}'
  AND user_status = 'T'
GROUP BY user_age_group
ORDER BY user_cnt DESC;
```

### 4.2 查询港漂用户画像
```sql
-- 查询港漂用户的性别和年龄分布
SELECT 
    user_gender,
    user_age_group,
    COUNT(DISTINCT user_id) AS user_cnt
FROM antsg_asap.adm_asap_base_user_label_dd
WHERE dt = '${bizdate}'
  AND is_hk_drifter = 'CX'
  AND user_status = 'T'
GROUP BY user_gender, user_age_group
ORDER BY user_cnt DESC;
```

### 4.3 查询高价值用户特征
```sql
-- 查询高价值用户的生命周期分布
SELECT 
    life_cycle,
    COUNT(DISTINCT user_id) AS user_cnt
FROM antsg_asap.adm_asap_base_user_label_dd
WHERE dt = '${bizdate}'
  AND user_value LIKE '1%'
  AND is_promo_black_flag = '0'
  AND is_black_list = '0'
GROUP BY life_cycle
ORDER BY user_cnt DESC;
```

### 4.4 查询KYC认证情况
```sql
-- 查询各KYC等级的用户分布
SELECT 
    kyc_level,
    COUNT(DISTINCT user_id) AS user_cnt
FROM antsg_asap.adm_asap_base_user_label_dd
WHERE dt = '${bizdate}'
  AND user_status = 'T'
GROUP BY kyc_level
ORDER BY user_cnt DESC;
```

### 4.5 查询用户地理位置分布
```sql
-- 查询近30天活跃区域分布
SELECT 
    active_region_r30d,
    COUNT(DISTINCT user_id) AS user_cnt
FROM antsg_asap.adm_asap_base_user_label_dd
WHERE dt = '${bizdate}'
  AND active_region_r30d IS NOT NULL
GROUP BY active_region_r30d
ORDER BY user_cnt DESC;
```

## 五、注意事项
1. **分区字段必填**：所有查询必须指定 `dt` 分区，格式为 `yyyyMMdd`
2. **用户状态过滤**：统计活跃用户数时，建议添加 `user_status = 'T'` 过滤正常用户
3. **营销黑名单过滤**：营销场景需排除黑名单用户，添加条件：

```sql
AND is_promo_black_flag = '0' 
AND is_black_list = '0'
```

4. **年龄计算**：`user_age = -1` 表示未获取到年龄，统计平均年龄时需排除
5. **生命周期字段说明**：
    - '1': 新手期用户
    - '2': 成长期用户  
    - '3': 成熟期用户
    - '4': 衰退期用户
    - '5': 沉默期用户
    - '6': 流失期用户
    - '61': 流失期用户_非AAU
6. **用户价值字段说明**：以'1'开头表示高价值用户，'8'开头表示低价值用户
7. **活跃区域字段**：包含内地、香港、日本、澳门、泰国、菲律宾、台湾、韩国、英国、马来西亚、新加坡、越南、印度尼西亚、缅甸、柬埔寨等
8. **风控评分字段**：
    - `pl_apply_predict_score`: 标准用户信贷评分，默认9999
    - `pl_apply_predict_score_ph_maid`: 菲佣用户信贷评分，默认9999
    - `pl_apply_user_rank`: 10分制评分，无得分为9999
    - `ploan_riskseg`: PloanA卡评级，范围0-9，默认999
    - `mcard_riskseg`: M卡评级，范围0-9，默认999
