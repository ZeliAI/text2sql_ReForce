import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from profile_agent import load_jsonl
from profile_sql_validator import validate_sql


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVAL_PATH = REPO_ROOT / "data" / "profile_eval" / "profile_text2sql_eval.jsonl"
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "profile_eval" / "profile_schema_registry.json"


def load_sample_log(sample_dir: Path) -> dict[str, Any]:
    log_path = sample_dir / "log.json"
    if log_path.exists():
        return json.loads(log_path.read_text(encoding="utf-8"))
    validation_path = sample_dir / "validation.json"
    selector_path = sample_dir / "selector.json"
    return {
        "id": sample_dir.name,
        "question": "",
        "difficulty": "",
        "validation": json.loads(validation_path.read_text(encoding="utf-8")) if validation_path.exists() else {},
        "selected_candidate": json.loads(selector_path.read_text(encoding="utf-8")).get("selected_candidate", "")
        if selector_path.exists()
        else "",
    }


def issue_summary(logs: list[dict[str, Any]]) -> Counter:
    counter = Counter()
    for log in logs:
        for issue in log.get("validation", {}).get("issues", []):
            counter[f"{issue['severity']}:{issue['code']}"] += 1
    return counter


def status_summary(logs: list[dict[str, Any]]) -> Counter:
    return Counter(log.get("validation", {}).get("status", "missing") for log in logs)


def candidate_summary(logs: list[dict[str, Any]]) -> Counter:
    counter = Counter()
    for log in logs:
        candidates = log.get("candidates", [])
        counter["total_candidates"] += len(candidates)
        for candidate in candidates:
            counter[f"candidate_status:{candidate.get('validation', {}).get('status', 'missing')}"] += 1
    return counter


def difficulty_summary(logs: list[dict[str, Any]]) -> dict[str, Counter]:
    result: dict[str, Counter] = defaultdict(Counter)
    for log in logs:
        difficulty = log.get("difficulty", "未知")
        status = log.get("validation", {}).get("status", "missing")
        result[difficulty][status] += 1
        result[difficulty]["total"] += 1
    return result


def issue_category(code: str) -> str:
    if code == "EMPTY_SQL":
        return "空 SQL / 抽取失败"
    if code in {"JOIN_WITHOUT_DT_BUT_FILTERED", "POSSIBLE_INCOMPLETE_DT", "MISSING_JOIN_DT"}:
        return "JOIN dt 静态检查"
    if code in {"UNKNOWN_IDENTIFIER", "UNKNOWN_COLUMN_FOR_TABLE", "UNKNOWN_TABLE", "NO_TABLE"}:
        return "字段/表选择风险"
    if code in {"COUNT_WITHOUT_DISTINCT_USER", "TOP_WITHOUT_LIMIT"}:
        return "指标口径 / 结果形态"
    return "其他静态规则"


def category_summary(logs: list[dict[str, Any]]) -> Counter:
    counter = Counter()
    for log in logs:
        seen = set()
        for item in log.get("validation", {}).get("issues", []):
            category = issue_category(item["code"])
            seen.add(category)
        for category in seen:
            counter[category] += 1
    return counter


def revalidate_logs(logs: list[dict[str, Any]], run_dir: Path, registry: dict[str, Any]) -> list[dict[str, Any]]:
    updated = []
    for log in logs:
        sample_id = log.get("id", "")
        sql_path = run_dir / sample_id / "result.sql"
        if not sql_path.exists():
            updated.append(log)
            continue
        item = dict(log)
        item["validation"] = validate_sql(sql_path.read_text(encoding="utf-8"), registry, item.get("question", ""))
        updated.append(item)
    return updated


def expected_table_text(eval_records: dict[str, dict[str, Any]], sample_id: str) -> str:
    record = eval_records.get(sample_id, {})
    return record.get("expected_analysis", {}).get("table_selection", "")


def render_report(logs: list[dict[str, Any]], eval_records: dict[str, dict[str, Any]], output_dir: Path) -> str:
    status_counter = status_summary(logs)
    issue_counter = issue_summary(logs)
    category_counter = category_summary(logs)
    candidate_counter = candidate_summary(logs)
    diff_counter = difficulty_summary(logs)

    total = len(logs)
    pass_count = status_counter.get("pass", 0)
    warning_count = status_counter.get("warning", 0)
    fail_count = status_counter.get("fail", 0)
    static_ok = pass_count + warning_count
    static_ok_rate = static_ok / total if total else 0

    lines = [
        "# 画像域 Text2SQL P0.7 Baseline 静态评测报告",
        "",
        "## 说明",
        "",
        "当前没有真实数据，本报告不评估执行结果正确性，只评估链路可运行性、SQL 静态质量和可审查性。",
        "",
        "## 汇总",
        "",
        f"- 输出目录：`{output_dir}`",
        f"- 样本数：{total}",
        f"- 静态通过：{pass_count}",
        f"- 静态警告：{warning_count}",
        f"- 静态失败：{fail_count}",
        f"- 静态可接受率：{static_ok_rate:.1%}",
        f"- 候选总数：{candidate_counter.get('total_candidates', 0)}",
        "",
        "## 按难度统计",
        "",
        "| 难度 | 总数 | pass | warning | fail |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for difficulty in ["简单", "中等", "困难", "未知"]:
        counter = diff_counter.get(difficulty)
        if not counter:
            continue
        lines.append(
            f"| {difficulty} | {counter.get('total', 0)} | {counter.get('pass', 0)} | {counter.get('warning', 0)} | {counter.get('fail', 0)} |"
        )

    lines.extend(["", "## 错误与警告类型", ""])
    if issue_counter:
        lines.extend(["| 类型 | 次数 |", "| --- | ---: |"])
        for key, count in issue_counter.most_common():
            lines.append(f"| `{key}` | {count} |")
    else:
        lines.append("- 未发现静态校验问题")

    lines.extend(["", "## 错误归因分组", ""])
    if category_counter:
        lines.extend(["| 分组 | 影响样本数 |", "| --- | ---: |"])
        for key, count in category_counter.most_common():
            lines.append(f"| {key} | {count} |")
    else:
        lines.append("- 未发现需要归因的问题")

    lines.extend(
        [
            "",
            "## 样本明细",
            "",
            "| ID | 难度 | 静态状态 | 选择候选 | 问题 | 预期选表分析 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for log in sorted(logs, key=lambda item: item.get("id", "")):
        sample_id = log.get("id", "")
        question = (log.get("question") or "").replace("|", "\\|")
        table_text = expected_table_text(eval_records, sample_id).replace("|", "\\|")
        lines.append(
            f"| {sample_id} | {log.get('difficulty', '')} | {log.get('validation', {}).get('status', 'missing')} | "
            f"{log.get('selected_candidate', '')} | {question} | {table_text} |"
        )

    lines.extend(["", "## 下一步建议", ""])
    if fail_count:
        lines.append("1. 优先查看 fail 样本的 `validation.md`，区分真实 SQL 风险和校验器白名单缺口。")
    if warning_count:
        lines.append("2. 对 warning 样本人工审查业务口径，决定是修 prompt 还是放宽静态规则。")
    lines.append("3. 抽样人工对照 `expected_analysis`，重点看表选择、字段映射、JOIN 和聚合口径。")
    lines.append("4. 后续如补 mock 数据，再增加执行结果级评测。")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a static baseline report for profile-domain Text2SQL runs.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--eval-path", type=Path, default=DEFAULT_EVAL_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--revalidate", action="store_true", help="Re-run static validation from result.sql using the current validator.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    eval_records = {record["id"]: record for record in load_jsonl(args.eval_path)}
    logs = [load_sample_log(path) for path in sorted(args.run_dir.iterdir()) if path.is_dir() and path.name.startswith("U")]
    if args.revalidate:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        logs = revalidate_logs(logs, args.run_dir, registry)
    report = render_report(logs, eval_records, args.run_dir)
    output_path = args.output or (args.run_dir / "baseline_report.md")
    output_path.write_text(report, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
