# Legacy ReFoRCE / Spider Code

V1.1 起，线上 Text2SQL agent 新代码已经上提到仓库根目录的 `online_agent/`、`run_online_agent.py`、`build_domain_registry.py`。旧 ReFoRCE / Spider2 榜单链路暂时保留在 `methods/ReFoRCE/` 和 `spider2-*` 目录中。

清理原则：

1. 新线上链路不再新增对 Spider2、Snow、OmniSQL 入口的依赖。
2. 已经用于画像域 baseline 的 `profile_*` 文件先保留，作为 V1.0 可复现实验。
3. 后续移动 legacy 文件时，按“先文档标记、再迁移 import、最后删除入口脚本”的顺序处理。
4. 工程同学开发线上 agent 时优先看仓库根目录的 `run_online_agent.py`、`build_domain_registry.py` 和 `online_agent/`。
