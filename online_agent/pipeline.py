import json
import re
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from online_agent.clarifier import clarify_or_continue
from online_agent.config import node_llm_config
from online_agent.context_builder import build_compact_context
from online_agent.date_adjuster import adjust_question_dates
from online_agent.domain_router_prompt import build_domain_router_prompt
from online_agent.llm import llm_for
from online_agent.prompts import build_schema_summary_prompt, build_selector_prompt, build_sql_prompt
from online_agent.registry import load_domain_registry
from online_agent.router import RouteResult, route_question
from online_agent.safety import apply_safety_guard
from online_agent.summary_guard import validate_schema_summary_fields
from online_agent.utils import (
    extract_selected_candidate,
    extract_sql,
    select_by_validation,
)
from sql_validator import validate_sql


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _timed_llm_call(chat, prompt: str, node: str, timings: list[dict[str, Any]], extra: Optional[dict[str, Any]] = None) -> str:
    started_at = now_iso()
    start = time.perf_counter()
    try:
        response = chat.get_model_response_txt(prompt)
        return response
    finally:
        elapsed = time.perf_counter() - start
        timing = {
            "node": node,
            "provider": getattr(chat, "provider", ""),
            "model": getattr(chat, "model", ""),
            "temperature": getattr(chat, "temperature", None),
            "started_at": started_at,
            "ended_at": now_iso(),
            "elapsed_seconds": round(elapsed, 3),
        }
        if extra:
            timing.update(extra)
        timings.append(timing)


def _generate_candidate(
    chat,
    sql_prompt: str,
    registry: dict[str, Any],
    question: str,
    safety_config: dict[str, Any],
    timings: list[dict[str, Any]],
    candidate_index: int,
) -> dict[str, Any]:
    raw_sql_response = _timed_llm_call(
        chat,
        sql_prompt,
        "sql_generation",
        timings,
        {"candidate": f"candidate_{candidate_index}"},
    ).strip()
    sql = extract_sql(raw_sql_response)
    validation = validate_sql(sql, registry, question)
    safety = apply_safety_guard(sql, validation, safety_config)
    if safety.sql != sql:
        sql = safety.sql
        validation = validate_sql(sql, registry, question)
    return {
        "sql": sql,
        "validation": validation,
        "safety": asdict(safety),
        "raw_sql_response": raw_sql_response,
    }


def _select_candidate(
    config: dict[str, Any],
    question: str,
    schema_summary: str,
    candidates: list[dict[str, Any]],
    use_selector: bool,
    timings: list[dict[str, Any]],
    registry: dict[str, Any],
) -> tuple[int, str, str]:
    selected_index = select_by_validation(candidates)
    selector_response = ""
    selector_reason = ""
    if use_selector and len(candidates) > 1:
        selector_config = node_llm_config(config, "selector")
        selector_chat = llm_for(selector_config)
        selector_prompt = build_selector_prompt(question, schema_summary, candidates, registry)
        selector_response = _timed_llm_call(selector_chat, selector_prompt, "selector", timings).strip()
        selected = extract_selected_candidate(selector_response, len(candidates))
        selected_index = selected - 1 if selected else selected_index
        reason_match = re.search(r"\[reason\]\s*(.*)", selector_response, flags=re.IGNORECASE | re.DOTALL)
        selector_reason = reason_match.group(1).strip() if reason_match else selector_response

    static_best_index = select_by_validation(candidates)
    if candidates[selected_index]["validation"]["status"] == "fail" and candidates[static_best_index]["validation"]["status"] != "fail":
        selector_reason = (
            (selector_reason + "\n\n" if selector_reason else "")
            + f"系统保护：selector 选择了 candidate_{selected_index + 1}，但该候选静态校验为 fail；"
            + f"已自动回退到 candidate_{static_best_index + 1}。"
        )
        selected_index = static_best_index
    return selected_index, selector_response, selector_reason


DOMAIN_OUTPUT_TO_KEY = {
    "画像域": "profile",
    "投放域": "marketing",
    "push域": "push",
    "PUSH域": "push",
    "策略域": "strategy",
}


def _normalize_router_output(raw_output: str) -> str:
    normalized = raw_output.strip()
    normalized = re.sub(r"^[`'\"\s，。:：]+|[`'\"\s，。:：]+$", "", normalized)
    normalized = normalized.replace(" ", "")
    for label in DOMAIN_OUTPUT_TO_KEY:
        if label.lower() in normalized.lower():
            return label
    return normalized


def _load_router_registries(config: dict[str, Any]) -> list[dict[str, Any]]:
    registries = []
    for domain in ("profile", "marketing", "push"):
        try:
            registries.append(load_domain_registry(config, domain))
        except (FileNotFoundError, KeyError):
            continue
    return registries


def _route_domain(config: dict[str, Any], question: str, timings: list[dict[str, Any]]) -> tuple[RouteResult, dict[str, Any]]:
    default_domain = config.get("default_domain", "profile")
    rule_route = route_question(question, default_domain=default_domain)
    router_config = config.get("router", {})
    if router_config.get("mode", "rule") != "llm":
        return rule_route, {
            "source": "rule",
            "rule_route": asdict(rule_route),
        }

    registries = _load_router_registries(config)
    if not registries:
        return rule_route, {
            "source": "rule_fallback",
            "fallback_reason": "no_registry_loaded",
            "rule_route": asdict(rule_route),
        }

    llm_config = node_llm_config(config, "router")
    router_chat = llm_for(llm_config)
    prompt = build_domain_router_prompt(question, registries)
    try:
        raw_output = _timed_llm_call(router_chat, prompt, "domain_router", timings).strip()
    except (Exception, SystemExit) as exc:
        return rule_route, {
            "source": "rule_fallback",
            "fallback_reason": f"llm_router_error: {type(exc).__name__}: {exc}",
            "rule_route": asdict(rule_route),
        }

    domain_label = _normalize_router_output(raw_output)
    domain = DOMAIN_OUTPUT_TO_KEY.get(domain_label)
    if not domain:
        return rule_route, {
            "source": "rule_fallback",
            "fallback_reason": f"invalid_llm_router_output: {raw_output}",
            "llm_raw_output": raw_output,
            "rule_route": asdict(rule_route),
        }

    route = RouteResult(
        route_type="single_domain",
        domains=[domain],
        confidence=0.85,
        reason=f"LLM router selected {domain_label}.",
    )
    return route, {
        "source": "llm",
        "llm_raw_output": raw_output,
        "domain_label": domain_label,
        "rule_route": asdict(rule_route),
    }


def run_online_one(config: dict[str, Any], record: dict[str, Any], use_selector: bool = True) -> dict[str, Any]:
    item_start = time.perf_counter()
    item_started_at = now_iso()
    timings: list[dict[str, Any]] = []
    question = record["question"]
    route, route_debug = _route_domain(config, question, timings)
    clarify = clarify_or_continue(question)
    if clarify.action != "continue":
        elapsed = time.perf_counter() - item_start
        return {
            "id": record.get("id", ""),
            "question": question,
            "route": asdict(route),
            "route_debug": route_debug,
            "clarify": asdict(clarify),
            "status": clarify.action,
            "sql": "",
            "candidates": [],
            "timing": {
                "started_at": item_started_at,
                "ended_at": now_iso(),
                "elapsed_seconds": round(elapsed, 3),
                "llm_calls": timings,
            },
        }

    if route.route_type == "mixed_domain":
        elapsed = time.perf_counter() - item_start
        return {
            "id": record.get("id", ""),
            "question": question,
            "route": asdict(route),
            "route_debug": route_debug,
            "clarify": asdict(clarify),
            "status": "clarify",
            "sql": "",
            "candidates": [],
            "message": "当前链路先处理单域问题；混合域问题需要后续接入跨域 context 和 SQL 生成策略。",
            "timing": {
                "started_at": item_started_at,
                "ended_at": now_iso(),
                "elapsed_seconds": round(elapsed, 3),
                "llm_calls": timings,
            },
        }

    domain = route.domains[0]
    registry = load_domain_registry(config, domain)
    date_adjust = adjust_question_dates(question)
    adjusted_question = date_adjust.question

    context_payload = build_compact_context(adjusted_question, registry)
    context_text = context_payload["context_text"]

    summary_config = node_llm_config(config, "schema_summary")
    summary_chat = llm_for(summary_config)
    schema_summary = _timed_llm_call(
        summary_chat,
        build_schema_summary_prompt(adjusted_question, context_text, registry),
        "schema_summary",
        timings,
    ).strip()
    summary_guard = validate_schema_summary_fields(schema_summary, registry)
    if summary_guard["status"] != "pass":
        elapsed = time.perf_counter() - item_start
        missing = ", ".join(summary_guard["unknown_fields"])
        return {
            "id": record.get("id", ""),
            "difficulty": record.get("difficulty", ""),
            "question": question,
            "adjusted_question": adjusted_question,
            "route": asdict(route),
            "route_debug": route_debug,
            "clarify": asdict(clarify),
            "date_adjust": asdict(date_adjust),
            "schema_summary": schema_summary,
            "schema_summary_guard": summary_guard,
            "sql": f"-- 目前用户查询无法满足：Schema Summary 引用了当前{registry.get('domain', '主题域')} registry 不存在的字段：{missing};",
            "validation": {
                "status": "fail",
                "error_count": 1,
                "warning_count": 0,
                "table_refs": [],
                "issues": [
                    {
                        "severity": "error",
                        "code": "SCHEMA_SUMMARY_UNKNOWN_FIELD",
                        "message": "Schema Summary 引用了当前 registry 不存在的字段，已阻断 SQL 生成。",
                        "evidence": missing,
                    }
                ],
            },
            "safety": {"status": "fail", "issues": [], "sql": ""},
            "candidates": [],
            "selected_candidate": "",
            "selector_response": "",
            "selector_reason": "",
            "context_tables": context_payload["context_tables"],
            "status": "fail",
            "timing": {
                "started_at": item_started_at,
                "ended_at": now_iso(),
                "elapsed_seconds": round(elapsed, 3),
                "llm_calls": timings,
            },
        }

    sql_config = node_llm_config(config, "sql_generation")
    sql_chat = llm_for(sql_config)
    sql_prompt = build_sql_prompt(adjusted_question, context_text, schema_summary, registry)
    candidates = [
        _generate_candidate(
            sql_chat,
            sql_prompt,
            registry,
            adjusted_question,
            config.get("safety", {}),
            timings,
            index,
        )
        for index in range(1, max(1, sql_config.num_candidates) + 1)
    ]
    selected_index, selector_response, selector_reason = _select_candidate(
        config, adjusted_question, schema_summary, candidates, use_selector, timings, registry
    )
    selected_candidate = candidates[selected_index]
    elapsed = time.perf_counter() - item_start
    return {
        "id": record.get("id", ""),
        "difficulty": record.get("difficulty", ""),
        "question": question,
        "adjusted_question": adjusted_question,
        "route": asdict(route),
        "route_debug": route_debug,
        "clarify": asdict(clarify),
        "date_adjust": asdict(date_adjust),
        "schema_summary": schema_summary,
        "schema_summary_guard": summary_guard,
        "sql": selected_candidate["sql"],
        "validation": selected_candidate["validation"],
        "safety": selected_candidate["safety"],
        "candidates": candidates,
        "selected_candidate": f"candidate_{selected_index + 1}",
        "selector_response": selector_response,
        "selector_reason": selector_reason,
        "context_tables": context_payload["context_tables"],
        "status": selected_candidate["validation"]["status"],
        "timing": {
            "started_at": item_started_at,
            "ended_at": now_iso(),
            "elapsed_seconds": round(elapsed, 3),
            "llm_calls": timings,
        },
    }


def write_online_output(item: dict[str, Any], output_dir: Path) -> Path:
    sample_id = item.get("id") or "interactive"
    sample_dir = output_dir / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)
    (sample_dir / "log.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    (sample_dir / "result.sql").write_text((item.get("sql") or "") + "\n", encoding="utf-8")
    if item.get("schema_summary"):
        (sample_dir / "schema_summary.md").write_text(item["schema_summary"] + "\n", encoding="utf-8")
    return sample_dir
