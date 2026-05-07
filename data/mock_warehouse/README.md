# Mock Online Warehouse

V1.1 先预留线上数据模拟入口，V1.3 再补完整执行器和更系统的样本构造。

目标：

1. 用小规模 CSV 验证 SQL 结果形态。
2. 覆盖 `user_id + dt` JOIN、`dt = max_pt(...)`、聚合、比例和 LIMIT。
3. 给 selector 预留可选的 mock 执行结果信号。
4. 与真实线上表名保持一一对应，便于后续替换成 DuckDB / SQLite 执行层。

