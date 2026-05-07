# adm_asap_other_action_user_label_dd（用户非交易行为画像表）

## 一、表信息
| 项目 | 内容 |
| --- | --- |
| 表名 | adm_asap_other_action_user_label_dd |
| 库名 | antsg_asap |
| 完整路径 | antsg_asap.adm_asap_other_action_user_label_dd |
| 表类型 | ADM 汇总表 |
| 数据更新频率 | 日更新（T+1） |
| 分区字段 | dt（格式：yyyyMMdd） |
| 数据生命周期 | 365天 |


## 二、表描述
用户非交易行为画像表，包含用户登录、活跃、领券、核销、关注商户等非交易行为标签。该表记录用户的非交易行为特征，包括APP访问、权益领取、商户关注、积分使用等行为，为用户运营、精准营销提供数据支持。

## 三、字段列表

> 注：由于该表字段较多（200+字段），以下列出核心字段分类，完整字段列表请参考语雀原文档。

### 3.1 登录活跃字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| user_active_r3d | 最近3天活跃天数 | STRING | 最近3天活跃天数，默认0 |
| user_active_r7d | 最近7天活跃天数 | STRING | 最近7天活跃天数，默认0 |
| user_active_r30d | 最近30天活跃天数 | STRING | 最近30天活跃天数，默认0 |
| login_cnt_r1d | 近1日登录次数 | BIGINT | 近1日登录次数，无登陆是0 |
| login_cnt_r7d | 7日内登录次数 | BIGINT | 7日内登录次数，无登陆是0 |
| login_cnt_r30d | 30日内登录次数 | BIGINT | 30日内登录次数，无登陆是0 |
| user_activity_level | 用户活跃等级 | STRING | 用户活跃等级(低频,中频,高频,沉默,流失,其它) |
| user_login_frequency | 用户登录频次 | STRING | 用户登录频次(上升,保持,下降) |
| is_7d_active | 近7天是否活跃 | STRING | 近7天是否活跃('1':是, '0':否) |
| is_30d_active | 近30天是否活跃 | STRING | 近30天是否活跃('1':是, '0':否) |

### 3.2 领券核销字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| send_cnt_r1d | 用户最近1天领券数量 | BIGINT | 用户最近1天领券数量 |
| send_cnt_r7d | 用户最近7天领券数量 | BIGINT | 用户最近7天领券数量 |
| send_cnt_r30d | 用户最近30天领券数量 | BIGINT | 用户最近30天领券数量 |
| use_cnt_r1d | 用户最近1天核销券数量 | BIGINT | 用户最近1天核销券数量 |
| use_cnt_r7d | 用户最近7天核销券数量 | BIGINT | 用户最近7天核销券数量 |
| use_cnt_r30d | 用户最近30天核销券数量 | BIGINT | 用户最近30天核销券数量 |

### 3.3 权益领取字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| equity_send_cnt_pts_r7d | 用户过去7天在积分权益的领取次数 | BIGINT | 用户过去7天在积分权益的领取次数 |
| equity_use_cnt_pts_r7d | 用户过去7天在积分权益的核销次数 | BIGINT | 用户过去7天在积分权益的核销次数 |
| equity_send_cnt_rp_r7d | 用户过去7天在红包权益的领取次数 | BIGINT | 用户过去7天在红包权益的领取次数 |
| equity_use_cnt_rp_r7d | 用户过去7天在红包权益的核销次数 | BIGINT | 用户过去7天在红包权益的核销次数 |
| equity_send_cnt_pts_r30d | 用户过去30天在积分权益的领取次数 | BIGINT | 用户过去30天在积分权益的领取次数 |
| equity_use_cnt_pts_r30d | 用户过去30天在积分权益的核销次数 | BIGINT | 用户过去30天在积分权益的核销次数 |

### 3.4 积分相关字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| is_point_new_user | 是否积分新用户 | STRING | 是否积分新用户(30天首次使用积分) ('1':是、'0:'否) |
| is_point_growing_user | 是否积分成长用户 | STRING | 是否积分成长用户('1':是、'0:'否) |
| is_point_active_user | 是否成熟积分用户 | STRING | 是否成熟积分用户('1':是、'0:'否) |
| is_point_lost_user | 是否积分流失用户 | STRING | 是否积分流失用户('1':是、'0:'否) |
| available_point_total | 总积分可用数量 | STRING | 总积分可用数量 |

### 3.5 Push互动字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| user_push_exposure_pv_r30d | 用户近30天push触达次数 | BIGINT | 用户近30天push触达次数(数值类型) |
| user_push_exposure_pv_r7d | 用户近7天push触达次数 | BIGINT | 用户近7天push触达次数(数值类型) |
| user_push_cilck_pv_r30d | 用户近30天push点击次数 | BIGINT | 用户近30天push点击次数(数值类型) |
| user_push_cilck_pv_r7d | 用户近7天push点击次数 | BIGINT | 用户近7天push点击次数(数值类型) |
| user_push_activity_level | 用户push活跃等级 | STRING | 用户push活跃等级(高频、中频、低频) |

### 3.6 页面点击字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| paper_clk_r7d | 最近7天腰封点击次数 | STRING | 最近7天腰封点击次数 |
| paper_clk_r30d | 最近30天腰封点击次数 | STRING | 最近30天腰封点击次数 |
| feeds_clk_r7d | 最近7天feeds点击次数 | STRING | 最近7天feeds点击次数 |
| feeds_clk_r30d | 最近30天feeds点击次数 | STRING | 最近30天feeds点击次数 |
| push_clk_r7d | 最近7天push点击次数 | STRING | 最近7天push点击次数 |
| push_clk_r30d | 最近30天push点击次数 | STRING | 最近30天push点击次数 |

### 3.7 商户关注字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| is_follow_food_effective_flag | 当前是否关注餐饮商户 | STRING | 当前是否关注餐饮商户 ('1':是、'0:'否) |
| is_follow_ent_effective_flag | 当前是否关注休闲娱乐商户 | STRING | 当前是否关注休闲娱乐商户 ('1':是、'0:'否) |
| is_follow_trans_effective_flag | 当前是否关注交通出行商户 | STRING | 当前是否关注交通出行商户 ('1':是、'0:'否) |
| follow_cnt_r7d | 过去7日关注商户数 | BIGINT | 过去7日关注商户数 |
| follow_cnt_r30d | 过去30日关注商户数 | BIGINT | 过去30日关注商户数 |


## 四、常用查询场景
### 4.1 查询用户活跃情况
```sql
SELECT 
    user_id,
    user_active_r7d,
    user_active_r30d,
    login_cnt_r7d,
    login_cnt_r30d,
    user_activity_level
FROM antsg_asap.adm_asap_other_action_user_label_dd
WHERE dt = '${bizdate}'
  AND user_active_r30d > 0
```

### 4.2 查询用户领券核销情况
```sql
SELECT 
    user_id,
    send_cnt_r7d,
    send_cnt_r30d,
    use_cnt_r7d,
    use_cnt_r30d
FROM antsg_asap.adm_asap_other_action_user_label_dd
WHERE dt = '${bizdate}'
  AND send_cnt_r30d > 0
```

### 4.3 查询用户关注商户情况
```sql
SELECT 
    user_id,
    is_follow_food_effective_flag,
    is_follow_ent_effective_flag,
    follow_cnt_r30d
FROM antsg_asap.adm_asap_other_action_user_label_dd
WHERE dt = '${bizdate}'
  AND follow_cnt_r30d > 0
```

### 4.4 查询积分用户分层
```sql
SELECT 
    user_id,
    is_point_new_user,
    is_point_active_user,
    is_point_lost_user,
    available_point_total
FROM antsg_asap.adm_asap_other_action_user_label_dd
WHERE dt = '${bizdate}'
  AND (is_point_new_user = '1' OR is_point_active_user = '1')
```

### 4.5 查询push触达情况
```sql
SELECT 
    user_id,
    user_push_exposure_pv_r7d,
    user_push_cilck_pv_r7d,
    user_push_activity_level
FROM antsg_asap.adm_asap_other_action_user_label_dd
WHERE dt = '${bizdate}'
  AND user_push_exposure_pv_r7d > 0
```


## 五、注意事项
1. **分区字段必填**：所有查询必须指定 `dt` 分区，格式为 `yyyyMMdd`
2. **布尔标志字段**：以 `is_` 开头的字段，'1' 表示是，'0' 表示否
3. **默认值说明**：
    - 活跃天数/次数类字段默认值为 0
    - 时间类字段无记录时默认值为 '9999-12-31 23:59:59'
    - 字符串类字段默认值为 null
4. **时间窗口字段**：
    - r1d/r7d/r15d/r30d/r60d/r90d/r365d 表示不同时间窗口的统计
    - his 表示历史至今的累计统计
5. **用户活跃等级**：user_activity_level 字段标识用户活跃程度（高频、中频、低频）
6. **积分用户分层**：包含新用户、成长用户、成熟用户、流失用户、沉默用户、潜在用户等分层
7. **数据更新**：该表按日更新，dt 分区为数据日期，通常 T+1 更新
8. **关联使用**：该表需与 `adm_asap_base_user_label_dd` 通过 `user_id` + `dt` 进行关联使用
