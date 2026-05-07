# Profile Mock Warehouse

画像域 mock 表与线上表保持同名文件：

| 线上表 | mock 文件 |
| --- | --- |
| `antsg_asap.adm_asap_base_user_label_dd` | `adm_asap_base_user_label_dd.csv` |
| `anthk_sg.adm_asap_algo_user_label_dd` | `adm_asap_algo_user_label_dd.csv` |
| `antsg_asap.adm_asap_pay_user_label_dd` | `adm_asap_pay_user_label_dd.csv` |
| `antsg_asap.adm_asap_other_action_user_label_dd` | `adm_asap_other_action_user_label_dd.csv` |

当前只放最小样例数据，用来验证 V1.1 入口和 join/partition 约束。

