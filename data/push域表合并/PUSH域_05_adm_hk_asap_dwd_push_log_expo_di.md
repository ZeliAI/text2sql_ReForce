# adm_hk_asap_dwd_push_log_expo_di（push曝光日志明细表）
> 返回 [push域 Schema 总览](./PUSH域_01_Schema总览.md)

---

## 一、表信息
| 属性 | 值 |
| --- | --- |
| 完整路径 | antsg_anthk_sg.adm_hk_asap_dwd_push_log_expo_di |
| 层级 | DWD（明细层） |
| 主键 | - (日志表无主键) |
| 外键 | delivery_push_task_id,creative_id → adm_hk_asap_dwd_push_task_info_dd |
| 分区 | dt (yyyyMMdd) |
| 说明 | push域曝光日志明细表，用于分析push消息的曝光效果 |

---

## 二、核心字段列表
## 维度字段
| 字段名 | 类型 | 描述 | 值域/示例 | 热度 |
| --- | --- | --- | --- | --- |
| loged_time | string | 上传服务器记录时间 | 2026-03-22 18:27:24.675 | ⚡ 中 |
| log_time | string | 客户端日志时间 | 2026-03-22 18:27:24.675 | �� 高 |
| alipay_product_id | string | 产品ID | WALLET_HK_ANDROID,WALLET_HK_IOS | �� 高 |
| alipay_product_version | string | 产品版本 | 10.3.96, 9.8.0 | ⚡ 中 |
| tcid | string | 设备id | 460000000000000\|nskvy9pm6ob500m | �� 高 |
| session_id | string | 会话id | 307B7E2F-AD1D-407B-AD48-8F6EB14B8D26 | �� 高 |
| user_id | string | 用户id(2088开头) | 2088222168756612 | �� 高 |
| behaviorid | string | 行为id(exposure) | exposure | �� 高 |
| spm | string | 曝光点的spm | a1.b2.c3.d4 | �� 高 |
| spm_a | string | 曝光点spm的a位 | a1 | ⚡ 中 |
| spm_b | string | 曝光点spm的b位 | b2 | ⚡ 中 |
| spm_c | string | 曝光点spm的c位 | c3 | ⚡ 中 |
| spm_d | string | 曝光点spm的d位 | d4 | ⚡ 中 |
| utdid | string | utdid | ZdKwcV9lBtsDAEQ5OubWwsdY | �� 高 |
| device_model | string | 设备号 | iPhone16 2 | ⚡ 中 |
| os_version | string | 操作系统版本 | 17.6.1 | ⚡ 中 |
| network | string | 网络 | LTE\|-- | ⚡ 中 |
| language | string | 语言 | zh-CN, en | ❄️ 低 |
| ip | string | ip | 192.168.1.1, 114.114... | ⚡ 中 |
| ip_country | string | 从ip中解析出来的国家名称 | 中国，USA | ❄️ 低 |
| ip_province | string | 从ip中解析出来的省份名称 | 浙江省，California | ❄️ 低 |
| ip_city | string | 从ip中解析出来的城市名称 | 杭州市，San Francisco | ❄️ 低 |
| log_type | string | 日志来源渠道 | native, h5, cashier | ⚡ 中 |
| experiment_ids | string | ABTest的实验id | exp_12345_groupB | ⚡ 中 |
| msg_id | string | ifcgotone的msgId | 2025072319117160175327073143434113170539031700053 | �� 高 |
| delivery_push_task_id | string | push任务ID | 外键→adm_hk_asap_dwd_push_task_info_dd<br/>示例：PUSH_TASK_ID20250723100019439 | 示例：DELIVERY_PUSH_TASK_20260322_001 |
| service_code | string | service code | GT_SC_alipayHK_push | ❄️ 低 |
| creative_id | string | 文案ID | STATIC_CONTENT20250723100037930 | ❄️ 低 |
| push_title | string | push的标题 | �� 只差一步！完成認證即可享有更多福利 | ⚡ 中 |
| push_sub_title | string | push的文本 | 快啲嚟解鎖專屬禮遇！立即認證 > | ⚡ 中 |
| push_url | string | push的uri,json格式 | | ❄️ 低 |
| dt | string | 时间分区 | 20260327 | �� 高 |

---

## 三、日志来源说明
log_type 字段枚举值：

- native：来自uniform_behavior的文件采集
- h5：来自webapp文件的采集
- cashier：来自收银台日志的采集

---

## 四、常用查询场景
### 4.1 统计曝光PV/UV
```sql
SELECT 
    dt,
    COUNT(*) AS expo_pv,
    COUNT(DISTINCT user_id) AS expo_uv
FROM adm_hk_asap_dwd_push_log_expo_di
WHERE dt = '${bizdate}'
GROUP BY dt
```

### 4.2 按任务统计曝光
```sql
SELECT 
    delivery_push_task_id,
    COUNT(*) AS expo_pv,
    COUNT(DISTINCT user_id) AS expo_uv
FROM adm_hk_asap_dwd_push_log_expo_di
WHERE dt = '${bizdate}'
GROUP BY delivery_push_task_id
```

### 4.3 按渠道统计曝光分布
```sql
SELECT 
    push_channel,
    COUNT(*) AS expo_pv,
    COUNT(DISTINCT user_id) AS expo_uv
FROM adm_hk_asap_dwd_push_log_expo_di
WHERE dt = '${bizdate}'
GROUP BY push_channel
```

---

## 五、注意事项
1. **分区字段**：dt (天分区) 为分区字段，查询时必须指定
2. **曝光定义**：曝光定义为push消息成功推送到用户终端并被展示
3. **关联维度**：通过 delivery_push_task_id 关联 push 任务核心宽表 `adm_hk_asap_dwd_push_task_info_dd` 获取任务详情
4. **数据来源**：数据来自埋点系统上报的曝光事件
