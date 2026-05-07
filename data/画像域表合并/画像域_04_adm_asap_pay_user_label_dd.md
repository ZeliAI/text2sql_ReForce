# adm_asap_pay_user_label_dd（用户交易行为画像表）

## 一、表信息
| 项目 | 内容 |
| --- | --- |
| 表名 | adm_asap_pay_user_label_dd |
| 库名 | antsg_asap |
| 完整路径 | antsg_asap.adm_asap_pay_user_label_dd |
| 表类型 | ADM 汇总表 |
| 数据更新频率 | 日更新（T+1） |
| 分区字段 | dt（格式：yyyyMMdd） |
| 数据生命周期 | 365天 |


## 二、表描述
用户交易行为画像表，包含用户绑卡、支付、充值、转账、理财等交易行为标签。该表记录用户的交易习惯、支付方式偏好、出行服务使用、金融理财行为等多维度交易特征，为用户运营、精准营销、风险控制提供数据支持。

## 三、字段列表

> 注：由于该表字段较多（300+字段），以下列出核心字段分类，完整字段列表请参考语雀原文档。

### 3.1 绑卡相关字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| is_bank_no | 是否绑定非直连银行 | STRING | 是否绑定非直连银行 ('1':是、'0:'否) |
| is_card_info | 是否绑卡 | STRING | 是否绑卡 ('1':是、'0:'否) |
| effective_bind_card_cnt | 当前有效绑卡数 | BIGINT | 当前有效绑卡数 |
| bind_card_cnt | 历史绑卡数 | BIGINT | 历史绑卡数 |
| is_bind_boci | 当前是否绑定中银信用卡 | STRING | 当前是否绑定中银信用卡('1':是、'0:'否) |
| is_bind_credit | 当前是否绑定VM或中银信用卡 | STRING | 当前是否绑定VM或中银信用卡('1':是、'0:'否) |
| is_bank_bind | 当前是否绑定银行卡 | STRING | 当前是否绑定银行卡('1':是、'0:'否) |
| is_bind_fps | 当前是否绑定FPS | STRING | 当前是否绑定FPS('1':是、'0:'否) |

### 3.2 交易行为字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| transact_amt_r1d | 最近1天内交易金额 | BIGINT | 最近1天内交易金额，默认0 |
| transact_amt_r7d | 最近7天内交易金额 | BIGINT | 最近7天内交易金额，默认0 |
| transact_amt_r30d | 最近30天内交易金额 | BIGINT | 最近30天内交易金额，默认0 |
| transact_num_r1d | 最近1天内交易次数 | BIGINT | 最近1天内交易次数，默认0 |
| transact_num_r7d | 最近7天内交易次数 | BIGINT | 最近7天内交易次数，默认0 |
| transact_num_r30d | 最近30天内交易次数 | BIGINT | 最近30天内交易次数，默认0 |
| pay_level_r30d | 用户近30天支付活跃分级 | STRING | G1-R30D高频次,高金额、G2-R30D高频次,中低金额...G9-R30D无支付活跃 |

### 3.3 交易场景字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| local_offline_scene_cnt_r30d | 最近30天交易笔数-本地線下 | BIGINT | 最近30天交易笔数-本地線下，默认0 |
| online_scene_cnt_r30d | 最近30天交易笔数-線上 | BIGINT | 最近30天交易笔数-線上，默认0 |
| transfer_scene_cnt_r30d | 最近30天交易笔数-轉賬 | BIGINT | 最近30天交易笔数-轉賬，默认0 |
| fee_payment_scene_cnt_r30d | 最近30天交易笔数-繳費 | BIGINT | 最近30天交易笔数-繳費，默认0 |
| crossborder_scene_cnt_r30d | 最近30天交易笔数-跨境線下 | BIGINT | 最近30天交易笔数-跨境線下，默认0 |
| transport_scene_cnt_r30d | 最近30天交易笔数-交通 | BIGINT | 最近30天交易笔数-交通，默认0 |
| finance_scene_cnt_r30d | 最近30天交易笔数-金融 | BIGINT | 最近30天交易笔数-金融，默认0 |

### 3.4 充值相关字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| topup_cnt_r1d | 1日充值笔数 | BIGINT | 1日充值笔数 |
| topup_cnt_r7d | 7日内充值笔数 | BIGINT | 7日内充值笔数 |
| topup_cnt_r30d | 30日内充值笔数 | BIGINT | 30日内充值笔数 |
| topup_amt_r1d | 1日充值金额 | BIGINT | 1日充值金额 |
| topup_amt_r7d | 7日内充值金额 | BIGINT | 7日内充值金额 |
| topup_amt_r30d | 30日内充值金额 | BIGINT | 30日内充值金额 |

### 3.5 出行服务字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| is_local_buscode | 是否開通本地乘車碼 | STRING | 是否開通本地乘車碼 ('1':是、'0:'否) |
| is_cross_buscode | 是否開通跨境乘車碼 | STRING | 是否開通跨境乘車碼 ('1':是、'0:'否) |
| is_auth_taxi | 是否授權打車 | STRING | 是否授權打車 ('1':是、'0:'否) |
| taxi_gaode_cnt_r30d | 最近30天使用高德打车次数 | BIGINT | 最近30天使用高德打车次数 |
| taxi_didi_cnt_r30d | 最近30天使用滴滴打车次数 | BIGINT | 最近30天使用滴滴打车次数 |
| high_rail_r30d | 最近30天乘坐高铁次数 | STRING | 最近30天乘坐高铁次数 |

### 3.6 eM+与理财字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| is_register_emplus | 是否开通eM+ | STRING | 是否开通eM+('1':是、'0:'否) |
| emplus_balance_amt_range | eM+余额区间 | BIGINT | eM+余额区间(元) |
| em_deposit_cnts_r30d | 用户最近30天入金次数 | BIGINT | 用户最近30天入金次数 |
| em_deposit_amounts_r30d | 用户最近30天入金金额 | STRING | 用户最近30天入金金额 |
| fund_holdings_amt | 个人持仓总值 | BIGINT | 个人持仓总值 |
| cur_fund_holdings_cnt | 当前持仓数量 | BIGINT | 当前持仓数量 |

### 3.7 缴费场景字段
| 字段名 | 字段中文名 | 字段类型 | 字段描述 |
| --- | --- | --- | --- |
| government_payment_r30 | 最近30天的政府缴费场景 | STRING | 水務署，薪俸稅，物業稅，學生還款，差餉，其他 |
| living_payment_r30 | 最近30天的生活缴费场景 | STRING | 電費_CLP，電費_港燈，煤氣費，管理費，大學繳費，其他 |
| telecom_payment_r30 | 最近30天的電讯缴费场景 | STRING | 香港寛頻，中置移動香港，3HK，數碼通，香港電訊HKT，電訊數碼，其他 |


## 四、常用查询场景
### 4.1 查询用户绑卡情况
```sql
SELECT 
    user_id,
    is_card_info,
    effective_bind_card_cnt,
    bind_card_cnt,
    is_bind_credit,
    is_bank_bind
FROM antsg_asap.adm_asap_pay_user_label_dd
WHERE dt = '${bizdate}'
  AND is_card_info = '1'
```

### 4.2 查询用户交易活跃度
```sql
SELECT 
    user_id,
    transact_num_r7d,
    transact_num_r30d,
    transact_amt_r7d,
    transact_amt_r30d,
    pay_level_r30d
FROM antsg_asap.adm_asap_pay_user_label_dd
WHERE dt = '${bizdate}'
  AND transact_num_r30d > 0
```

### 4.3 查询用户充值情况
```sql
SELECT 
    user_id,
    topup_cnt_r7d,
    topup_cnt_r30d,
    topup_amt_r7d,
    topup_amt_r30d
FROM antsg_asap.adm_asap_pay_user_label_dd
WHERE dt = '${bizdate}'
  AND topup_cnt_r30d > 0
```

### 4.4 查询用户理财情况
```sql
SELECT 
    user_id,
    is_register_emplus,
    emplus_balance_amt_range,
    fund_holdings_amt,
    cur_fund_holdings_cnt
FROM antsg_asap.adm_asap_pay_user_label_dd
WHERE dt = '${bizdate}'
  AND is_register_emplus = '1'
```


## 五、注意事项
1. **分区字段必填**：所有查询必须指定 `dt` 分区，格式为 `yyyyMMdd`
2. **布尔标志字段**：以 `is_` 开头的字段，'1' 表示是，'0' 表示否
3. **默认值说明**：
    - 交易笔数/金额类字段默认值为 0
    - 天数类字段无记录时默认值为 -1 或 9999
    - 字符串类字段默认值为 null
4. **时间窗口字段**：
    - r1d/r7d/r15d/r30d/r60d/r90d/r365d 表示不同时间窗口的统计
    - his 表示历史至今的累计统计
5. **支付活跃分级**：pay_level_r30d 字段将用户分为 G1-G9 九个等级，从高频高金额到无支付活跃
6. **数据更新**：该表按日更新，dt 分区为数据日期，通常 T+1 更新
7. **关联使用**：该表需与 `adm_asap_base_user_label_dd` 通过 `user_id` + `dt` 进行关联使用
