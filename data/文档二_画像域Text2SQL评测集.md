# 画像域 Text2SQL 评测集（30题）

> 基于画像域 4 张 ADM 表的真实 Schema 构造，覆盖简单（0-2分）/ 中等（3-4分）/ 困难（5-6分）各 10 题。  
所有字段和枚举值均可追溯到 Schema 文档。
>

## Schema 速查
| 表名 | 库名 | 核心能力 |
| --- | --- | --- |
| adm_asap_base_user_label_dd | antsg_asap | 用户基础画像（状态/年龄/性别/港漂/认证/设备/LBS/生命周期/价值/风控） |
| adm_asap_algo_user_label_dd | anthk_sg | 用户行为偏好（权益/展位/业务/品类/eM+/基金潜客/回流沉默预警） |
| adm_asap_pay_user_label_dd | antsg_asap | 用户交易行为（交易笔数/金额/场景/充值/绑卡/出行/理财） |
| adm_asap_other_action_user_label_dd | antsg_asap | 用户非交易行为（登录/活跃/领券/核销/push互动/商户关注/积分） |


**关联方式**：4 表平级，通过 `user_id` + `dt` JOIN（1:1）

---

## 简单（总分 0-2）
| 序号 | 难度 | 问题 | 维度A分析 | 维度B分析 | 维度C分析 | 总分 |
| --- | --- | --- | --- | --- | --- | --- |
| U001 | 简单 | 昨天iOS和安卓的用户各有多少 | "iOS"→u_os='IOS'（base表.u_os，枚举已验证）；"安卓"→u_os='ANDROID'（base表.u_os）；指标、时间、对象均明确，无歧义；A=0 | 单表查询：antsg_asap.adm_asap_base_user_label_dd；无需JOIN；B=0 | GROUP BY u_os + COUNT DISTINCT user_id，无子查询/窗口函数；C=0 | 0 |
| U002 | 简单 | 高价值用户里男女比例是多少 | "高价值"→user_value LIKE '1%'（base表.user_value，以'1'开头为高价值，枚举已验证）；"男女"→user_gender='F'/'M'（base表.user_gender）；轻度映射（user_value编码需理解）；A=1 | 单表查询：antsg_asap.adm_asap_base_user_label_dd；无需JOIN；B=0 | CASE WHEN计算男女各自COUNT + 比例，属中等聚合；C=1 | 2 |
| U003 | 简单 | 帮我看下各生命周期阶段的用户数 | "生命周期"→life_cycle（base表.life_cycle，'1':新手期, '2':成长期, '3':成熟期, '4':衰退期, '5':沉默期, '6':流失期, '61':流失期_非AAU）；"帮我看下"轻度口语；需理解枚举值含义；A=1 | 单表查询：antsg_asap.adm_asap_base_user_label_dd；无需JOIN；B=0 | GROUP BY life_cycle + COUNT DISTINCT，无子查询/窗口；C=0 | 1 |
| U004 | 简单 | eM+高潜用户目前有多少人 | "eM+高潜"→em_potential_segment='高潜'（algo表.em_potential_segment，枚举值：高潜/中潜/低潜，已验证）；需简单映射；A=1 | 单表查询：anthk_sg.adm_asap_algo_user_label_dd；无需JOIN；B=0 | WHERE + COUNT DISTINCT，无子查询/窗口；C=0 | 1 |
| U005 | 简单 | 港漂用户和永久居民各有多少 | "港漂"→is_hk_drifter='CX'（base表.is_hk_drifter，CX=非永久居民）；"永久居民"→is_hk_drifter='AX'（base表.is_hk_drifter，AX=永久居民）；需枚举映射；A=1 | 单表查询：antsg_asap.adm_asap_base_user_label_dd；无需JOIN；B=0 | GROUP BY is_hk_drifter + COUNT DISTINCT；C=0 | 1 |
| U006 | 简单 | 近30天本地线下交易超过5笔的用户有多少 | "本地线下交易"→local_offline_scene_cnt_r30d（pay表.local_offline_scene_cnt_r30d）；"超过5笔"→>5；指标、时间、条件均明确；A=0 | 单表查询：antsg_asap.adm_asap_pay_user_label_dd；无需JOIN；B=0 | WHERE条件 + COUNT DISTINCT，无子查询/窗口；C=0 | 0 |
| U007 | 简单 | 沉默风险高的用户有多少人 | "沉默风险高"→silence_risk_level='high'（algo表.silence_risk_level，枚举值：high/medium/low，已验证）；需简单映射；A=1 | 单表查询：anthk_sg.adm_asap_algo_user_label_dd；无需JOIN；B=0 | WHERE + COUNT DISTINCT；C=0 | 1 |
| U008 | 简单 | 积分偏好高的用户中，红包偏好也高的有多少 | "积分偏好高"→pts_prefer_level='high'（algo表.pts_prefer_level）；"红包偏好高"→rp_prefer_level='high'（algo表.rp_prefer_level）；两个偏好字段在同一张表，轻度映射；A=1 | 单表查询：anthk_sg.adm_asap_algo_user_label_dd（两字段均在algo表）；无需JOIN；B=0 | WHERE双条件 + COUNT DISTINCT；C=0 | 1 |
| U009 | 简单 | 各KYC认证等级的用户分布看下 | "KYC认证等级"→kyc_level（base表.kyc_level，枚举值：CDD0/CDD1/CDD2/EKYC/UNKNOWN_KYC_LEVEL，已验证）；"看下"轻度口语；需枚举映射；A=1 | 单表查询：antsg_asap.adm_asap_base_user_label_dd；无需JOIN；B=0 | GROUP BY kyc_level + COUNT DISTINCT；C=0 | 1 |
| U010 | 简单 | 近30天push触达次数最多的top10用户是谁 | "push触达次数"→user_push_exposure_pv_r30d（other_action表.user_push_exposure_pv_r30d，数值类型）；"最多的top10"语义明确但需排序；A=1 | 单表查询：antsg_asap.adm_asap_other_action_user_label_dd；无需JOIN；B=0 | ORDER BY DESC + LIMIT 10，属topN排序；C=1 | 2 |


---

## 中等（总分 3-4）
| 序号 | 难度 | 问题 | 维度A分析 | 维度B分析 | 维度C分析 | 总分 |
| --- | --- | --- | --- | --- | --- | --- |
| U011 | 中等 | 高价值用户中积分偏好高的有多少人，低价值用户中呢 | "高价值"→user_value LIKE '1%'（base表.user_value）；"低价值"→user_value LIKE '8%'（base表.user_value）；"积分偏好高"→pts_prefer_level='high'（algo表.pts_prefer_level）；轻度映射+口语"呢"；A=1 | 2张表：antsg_asap.adm_asap_base_user_label_dd（user_value） + anthk_sg.adm_asap_algo_user_label_dd（pts_prefer_level）；JOIN Key: user_id + dt；B=1 | CASE WHEN按user_value分组 + COUNT DISTINCT对比统计；C=1 | 3 |
| U012 | 中等 | 沉默期用户中回流潜力高的占比多少 | "沉默期"→life_cycle='5'（base表.life_cycle）；"回流潜力高"→reactivation_level='high'（algo表.reactivation_level，枚举已验证）；需跨表映射；A=1 | 2张表：antsg_asap.adm_asap_base_user_label_dd（life_cycle） + anthk_sg.adm_asap_algo_user_label_dd（reactivation_level）；JOIN Key: user_id + dt；B=1 | 子查询计算总沉默期人数 + JOIN后COUNT高回流人数 + 比例计算；C=1 | 3 |
| U013 | 中等 | 各年龄段用户近30天的平均交易金额是多少，哪个年龄段消费力最强 | "年龄段"→user_age_group（base表.user_age_group，枚举'0'-'9'）；"平均交易金额"→AVG(transact_amt_r30d)（pay表.transact_amt_r30d）；"消费力最强"轻度口语；A=1 | 2张表：antsg_asap.adm_asap_base_user_label_dd（user_age_group） + antsg_asap.adm_asap_pay_user_label_dd（transact_amt_r30d）；JOIN Key: user_id + dt；B=1 | AVG + GROUP BY + ORDER BY DESC，属排序聚合；C=1 | 3 |
| U014 | 中等 | 新手期用户中push互动高频的有多少人，他们主要在哪些区域活跃 | "新手期"→life_cycle='1'（base表.life_cycle）；"push互动高频"→user_push_activity_level='高频'（other_action表.user_push_activity_level，枚举值：高频/中频/低频，已验证）；需文档映射"高频"概念；"在哪些区域活跃"→active_region_r30d（base表）；A=2 | 2张表：antsg_asap.adm_asap_base_user_label_dd（life_cycle, active_region_r30d） + antsg_asap.adm_asap_other_action_user_label_dd（user_push_activity_level）；JOIN Key: user_id + dt；B=1 | JOIN + GROUP BY active_region_r30d + ORDER BY；C=1 | 4 |
| U015 | 中等 | eM+高潜和基金高潜的重叠用户有多少，他们的注册号码分布呢 | "eM+高潜"→em_potential_segment='高潜'（algo表）；"基金高潜"→fund_potential_segment='高潜'（algo表）；"重叠"需理解为双条件交集；"注册号码"→register_number（base表，'86'/'852'/'853'/'其他'）；A=2 | 2张表：anthk_sg.adm_asap_algo_user_label_dd（em_potential_segment, fund_potential_segment） + antsg_asap.adm_asap_base_user_label_dd（register_number）；JOIN Key: user_id + dt；B=1 | JOIN + 多WHERE条件 + GROUP BY register_number；C=1 | 4 |
| U016 | 中等 | 提频潜力高的用户近30天交易笔数和充值金额是什么水平 | "提频潜力高"→freq_uplift_level='high'（algo表.freq_uplift_level，枚举已验证）；"交易笔数"→transact_num_r30d（pay表）；"充值金额"→topup_amt_r30d（pay表）；需简单映射；A=1 | 2张表：anthk_sg.adm_asap_algo_user_label_dd（freq_uplift_level） + antsg_asap.adm_asap_pay_user_label_dd（transact_num_r30d, topup_amt_r30d）；JOIN Key: user_id + dt；B=1 | JOIN + AVG/SUM聚合；C=1 | 3 |
| U017 | 中等 | 近7天腰封点击超过3次的用户，他们的交易金额平均是多少 | "腰封点击"→paper_clk_r7d（other_action表.paper_clk_r7d，近7天腰封点击次数）；"交易金额"→transact_amt_r30d（pay表）；需简单映射；A=1 | 2张表：antsg_asap.adm_asap_other_action_user_label_dd（paper_clk_r7d） + antsg_asap.adm_asap_pay_user_label_dd（transact_amt_r30d）；JOIN Key: user_id + dt；B=1 | WHERE条件 + JOIN + AVG；C=1 | 3 |
| U018 | 中等 | 衰退期用户中近30天还有交易的人数占比多少，跟沉默期比呢 | "衰退期"→life_cycle='4'（base表）；"还有交易"→transact_num_r30d>0（pay表）；"跟沉默期比呢"→life_cycle='5'需对比，口语化"呢"；需理解生命周期枚举+交易活跃度概念；A=2 | 2张表：antsg_asap.adm_asap_base_user_label_dd（life_cycle） + antsg_asap.adm_asap_pay_user_label_dd（transact_num_r30d）；JOIN Key: user_id + dt；B=1 | CASE WHEN分两个人群 + 占比计算；C=1 | 4 |
| U019 | 中等 | 绑了3张以上卡的用户和只绑1张的，领券核销行为有啥差异 | "绑了3张以上卡"→effective_bind_card_cnt>=3（pay表）；"只绑1张"→effective_bind_card_cnt=1（pay表）；"领券"→send_cnt_r30d（other_action表）；"核销"→use_cnt_r30d（other_action表）；"有啥差异"口语化；需跨表理解行为差异；A=2 | 2张表：antsg_asap.adm_asap_pay_user_label_dd（effective_bind_card_cnt） + antsg_asap.adm_asap_other_action_user_label_dd（send_cnt_r30d, use_cnt_r30d）；JOIN Key: user_id + dt；B=1 | CASE WHEN分组 + AVG对比统计；C=1 | 4 |
| U020 | 中等 | 近30天push点击超过5次的用户，积分和红包偏好分布怎么样 | "push点击"→user_push_cilck_pv_r30d（other_action表，数值类型）；"积分偏好"→pts_prefer_level（algo表）；"红包偏好"→rp_prefer_level（algo表）；"怎么样"轻度口语；A=1 | 2张表：antsg_asap.adm_asap_other_action_user_label_dd（user_push_cilck_pv_r30d） + anthk_sg.adm_asap_algo_user_label_dd（pts_prefer_level, rp_prefer_level）；JOIN Key: user_id + dt；B=1 | JOIN + GROUP BY多偏好字段；C=1 | 3 |


---

## 困难（总分 5-6）
| 序号 | 难度 | 问题 | 维度A分析 | 维度B分析 | 维度C分析 | 总分 |
| --- | --- | --- | --- | --- | --- | --- |
| U021 | 困难 | eM+高潜且支付高频高金额的用户有多少，这批人的年龄和性别分布是什么样 | "eM+高潜"→em_potential_segment='高潜'（algo表）；"支付高频高金额"→pay_level_r30d='G1-R30D高频次,高金额'（pay表.pay_level_r30d，G1对应高频+高金额，需文档理解G分级）；"年龄和性别"→user_age_group, user_gender（base表）；多字段跨表，需文档依赖；A=2 | 3张表：anthk_sg.adm_asap_algo_user_label_dd（em_potential_segment） + antsg_asap.adm_asap_pay_user_label_dd（pay_level_r30d） + antsg_asap.adm_asap_base_user_label_dd（user_age_group, user_gender）；JOIN Key: user_id + dt；B=2 | 3表JOIN + GROUP BY年龄+性别；C=1 | 5 |
| U022 | 困难 | 沉默期+高回流潜力的用户，近30天交易金额和充值金额跟成长期用户比怎么样 | "沉默期"→life_cycle='5'（base表）；"高回流潜力"→reactivation_level='high'（algo表）；"成长期"→life_cycle='2'（base表）；"跟…比怎么样"强口语；需构造双人群对比，多业务概念依赖文档；A=2 | 3张表：antsg_asap.adm_asap_base_user_label_dd（life_cycle） + anthk_sg.adm_asap_algo_user_label_dd（reactivation_level） + antsg_asap.adm_asap_pay_user_label_dd（transact_amt_r30d, topup_amt_r30d）；B=2 | CTE构造双人群 + UNION ALL对比 + 多表JOIN，属分步聚合；C=2 | 6 |
| U023 | 困难 | 高价值港漂女性中eM+高营销敏感度的有多少，她们偏好什么权益 | "高价值"→user_value LIKE '1%'（base表）；"港漂"→is_hk_drifter='CX'（base表）；"女性"→user_gender='F'（base表）；"eM+高营销敏感度"→em_marketing_sensitivity='高营销敏感度'（algo表，枚举已验证）；"偏好什么权益"需看pts/rp/cou_prefer_level等多个偏好字段（algo表）；多重条件+依赖文档；A=2 | 2张表：antsg_asap.adm_asap_base_user_label_dd + anthk_sg.adm_asap_algo_user_label_dd；JOIN Key: user_id + dt；B=1 | 多CASE WHEN统计各偏好维度的高偏好人数 + ORDER BY选出最高偏好；C=2 | 5 |
| U024 | 困难 | 新手期用户中30天内线上交易超过10笔且push点击超过3次的，他们的年龄和注册来源分布 | "新手期"→life_cycle='1'（base表）；"线上交易"→online_scene_cnt_r30d（pay表）；"push点击"→user_push_cilck_pv_r30d（other_action表）；"年龄"→user_age_group（base表）；"注册来源"→register_from（base表）；多重跨表条件组合；A=2 | 3张表：antsg_asap.adm_asap_base_user_label_dd（life_cycle, user_age_group, register_from） + antsg_asap.adm_asap_pay_user_label_dd（online_scene_cnt_r30d） + antsg_asap.adm_asap_other_action_user_label_dd（user_push_cilck_pv_r30d）；B=2 | 3表JOIN + 多WHERE条件 + GROUP BY；C=1 | 5 |
| U025 | 困难 | 各生命周期用户的近7天和近30天交易笔数对比，哪个阶段交易在下滑 | "各生命周期"→life_cycle（base表，6个阶段）；"近7天交易笔数"→transact_num_r7d（pay表）；"近30天交易笔数"→transact_num_r30d（pay表）；"交易在下滑"需理解为7天占30天比例偏低=趋势下降，业务口径推断；A=2 | 2张表：antsg_asap.adm_asap_base_user_label_dd（life_cycle） + antsg_asap.adm_asap_pay_user_label_dd（transact_num_r7d, transact_num_r30d）；B=1 | 双时间窗口AVG对比 + 计算变化率 + 窗口函数RANK排序找下滑最严重的阶段；C=2 | 5 |
| U026 | 困难 | 沉默风险高且积分偏好也高的用户，他们的交易笔数和登录频率是什么水平 | "沉默风险高"→silence_risk_level='high'（algo表）；"积分偏好高"→pts_prefer_level='high'（algo表）；"交易笔数"→transact_num_r30d（pay表）；"登录频率"→login_cnt_r30d（other_action表）；多字段跨3表；A=2 | 3张表：anthk_sg.adm_asap_algo_user_label_dd（silence_risk_level, pts_prefer_level） + antsg_asap.adm_asap_pay_user_label_dd（transact_num_r30d） + antsg_asap.adm_asap_other_action_user_label_dd（login_cnt_r30d）；B=2 | 3表JOIN + AVG/SUM统计；C=1 | 5 |
| U027 | 困难 | push高频用户中高价值和低价值的近30天交易金额和充值笔数差多少，按年龄段拆开看 | "push高频"→user_push_activity_level='高频'（other_action表）；"高价值"→user_value LIKE '1%'（base表）；"低价值"→user_value LIKE '8%'（base表）；"交易金额"→transact_amt_r30d（pay表）；"充值笔数"→topup_cnt_r30d（pay表）；"按年龄段"→user_age_group（base表）；多重业务概念+口语"差多少"；A=2 | 3张表：antsg_asap.adm_asap_other_action_user_label_dd + antsg_asap.adm_asap_base_user_label_dd + antsg_asap.adm_asap_pay_user_label_dd；B=2 | CTE + CASE WHEN双人群 + GROUP BY年龄段 + 多指标对比，属分步聚合；C=2 | 6 |
| U028 | 困难 | 基金高潜用户的近30天充值行为跟非高潜用户比怎么样，按年龄段看 | "基金高潜"→fund_potential_segment='高潜'（algo表）；"充值行为"→topup_cnt_r30d, topup_amt_r30d（pay表）；"非高潜"→fund_potential_segment IN ('中潜','低潜')（algo表）；"按年龄段"→user_age_group（base表）；"跟…比怎么样"口语；A=2 | 3张表：anthk_sg.adm_asap_algo_user_label_dd + antsg_asap.adm_asap_pay_user_label_dd + antsg_asap.adm_asap_base_user_label_dd；B=2 | CTE构造双人群 + GROUP BY年龄段 + JOIN对比；C=1 | 5 |
| U029 | 困难 | 衰退期和沉默期用户中，近30天有领券但没核销的人占多少，这些"只领不用"的用户偏好什么权益 | "衰退期"→life_cycle='4'（base表）；"沉默期"→life_cycle='5'（base表）；"领券没核销"→send_cnt_r30d>0 AND use_cnt_r30d=0（other_action表）；"只领不用"口语化描述；"偏好什么权益"→需看pts/rp/cou_prefer_level等多个偏好字段（algo表）；A=2 | 3张表：antsg_asap.adm_asap_base_user_label_dd + antsg_asap.adm_asap_other_action_user_label_dd + anthk_sg.adm_asap_algo_user_label_dd；B=2 | CTE构造人群 + 占比计算 + 多CASE WHEN偏好分析，属分步聚合；C=2 | 6 |
| U030 | 困难 | 近30天登录超过10次但交易不到3笔的用户，他们的eM+潜客分层和沉默风险分布怎样 | "登录次数"→login_cnt_r30d（other_action表）；"交易笔数"→transact_num_r30d（pay表）；"eM+潜客分层"→em_potential_segment（algo表，高潜/中潜/低潜）；"沉默风险"→silence_risk_level（algo表，high/medium/low）；多字段跨3表；A=2 | 3张表：antsg_asap.adm_asap_other_action_user_label_dd（login_cnt_r30d） + antsg_asap.adm_asap_pay_user_label_dd（transact_num_r30d） + anthk_sg.adm_asap_algo_user_label_dd（em_potential_segment, silence_risk_level）；B=2 | 3表JOIN + GROUP BY双维度分布；C=1 | 5 |
