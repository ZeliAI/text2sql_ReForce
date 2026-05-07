# Legacy Spider / ReFoRCE Scripts

本目录最初来自 ReFoRCE 开源实现，包含公开榜单相关的 Spider2 / Snow / OmniSQL 代码。V1.1 线上化重构后，这些文件只作为论文复现和历史 baseline 参考。

线上业务链路入口：

```bash
python3 online_profile_agent.py --limit 1 --no-selector
```

V1.1 新代码位置：

```text
online_agent/
configs/online_agent_v1_1.json
online_profile_agent.py
```

后续清理时，Spider 相关脚本会迁移到 `methods/legacy_reforce/` 或从线上开发目录中移除。

