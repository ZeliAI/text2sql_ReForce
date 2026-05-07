import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from online_agent.config import DEFAULT_CONFIG_PATH, domain_config, load_config, resolve_path
from online_agent.pipeline import run_online_one, write_online_output
from profile_agent import load_jsonl


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def record_id(record: dict) -> str:
    return record.get("id") or "interactive"


def build_error_item(record: dict, error: BaseException, started_at: str, elapsed_seconds: float) -> dict:
    return {
        "id": record_id(record),
        "difficulty": record.get("difficulty", ""),
        "question": record.get("question", ""),
        "status": "error",
        "sql": "",
        "candidates": [],
        "message": f"{type(error).__name__}: {error}",
        "timing": {
            "started_at": started_at,
            "ended_at": now_iso(),
            "elapsed_seconds": round(elapsed_seconds, 3),
            "llm_calls": [],
        },
    }


def load_existing_item(output_dir: Path, sample_id: str) -> Optional[dict]:
    log_path = output_dir / sample_id / "log.json"
    if not log_path.exists():
        return None
    return json.loads(log_path.read_text(encoding="utf-8"))


def write_run_artifacts(output_dir: Path, outputs: list[dict], run_summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "run_summary.json").write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    timing_rows = []
    for item in outputs:
        timing = item.get("timing") or {}
        llm_calls = timing.get("llm_calls") or []
        timing_rows.append(
            {
                "id": item.get("id") or "interactive",
                "status": item.get("status"),
                "selected_candidate": item.get("selected_candidate", ""),
                "elapsed_seconds": timing.get("elapsed_seconds"),
                "llm_call_count": len(llm_calls),
                "llm_elapsed_seconds": round(sum(call.get("elapsed_seconds", 0) or 0 for call in llm_calls), 3),
                "llm_calls": llm_calls,
            }
        )
    (output_dir / "timing_report.json").write_text(json.dumps(timing_rows, ensure_ascii=False, indent=2), encoding="utf-8")


def append_event(output_dir: Path, event: dict) -> None:
    event = {"event_time": now_iso(), **event}
    with (output_dir / "run_events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run online Text2SQL chain.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path("output/online-v1_2-smoke"))
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--sample-ids", default="", help="Comma-separated ids such as U001,U004. Overrides limit/offset.")
    parser.add_argument("--question", default="", help="Run one interactive question instead of eval records.")
    parser.add_argument("--no-selector", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Reuse existing sample log.json files and skip model calls for completed records.")
    args = parser.parse_args()

    config = load_config(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.question:
        records = [{"id": "interactive", "question": args.question, "difficulty": ""}]
    else:
        profile = domain_config(config, "profile")
        eval_records = load_jsonl(resolve_path(profile["eval_path"]))
        if args.sample_ids:
            wanted = {item.strip() for item in args.sample_ids.split(",") if item.strip()}
            records = [record for record in eval_records if record["id"] in wanted]
        else:
            records = eval_records[args.offset : args.offset + args.limit]

    run_started_at = now_iso()
    run_start = time.perf_counter()
    outputs = []
    run_summary = {
        "status": "running",
        "started_at": run_started_at,
        "ended_at": "",
        "elapsed_seconds": 0,
        "record_count": 0,
        "planned_record_count": len(records),
        "output_dir": str(args.output_dir),
        "resume": bool(args.resume),
    }
    write_run_artifacts(args.output_dir, outputs, run_summary)
    append_event(args.output_dir, {"event": "run_start", "planned_record_count": len(records), "resume": bool(args.resume)})

    for index, record in enumerate(records, start=1):
        sample_id = record_id(record)
        reused = False
        if args.resume:
            item = load_existing_item(args.output_dir, sample_id)
            reused = item is not None
        else:
            item = None

        if item is None:
            record_started_at = now_iso()
            record_start = time.perf_counter()
            try:
                item = run_online_one(config, record, use_selector=not args.no_selector)
            except BaseException as exc:
                item = build_error_item(record, exc, record_started_at, time.perf_counter() - record_start)
        outputs.append(item)
        sample_dir = write_online_output(item, args.output_dir)
        elapsed = item.get("timing", {}).get("elapsed_seconds")
        elapsed_text = f" elapsed={elapsed:.3f}s" if isinstance(elapsed, (int, float)) else ""
        reused_text = " reused=true" if reused else ""
        print(
            f"[{now_iso()}] {sample_id} -> {sample_dir / 'result.sql'} "
            f"[{item.get('status')}] ({index}/{len(records)}){elapsed_text}{reused_text}"
        )
        append_event(
            args.output_dir,
            {
                "event": "record_done",
                "id": sample_id,
                "status": item.get("status"),
                "selected_candidate": item.get("selected_candidate", ""),
                "elapsed_seconds": elapsed,
                "reused": reused,
                "index": index,
                "total": len(records),
            },
        )
        run_summary.update(
            {
                "record_count": len(outputs),
                "ended_at": now_iso(),
                "elapsed_seconds": round(time.perf_counter() - run_start, 3),
            }
        )
        write_run_artifacts(args.output_dir, outputs, run_summary)

    run_elapsed = time.perf_counter() - run_start
    run_summary.update(
        {
            "status": "completed",
            "ended_at": now_iso(),
            "elapsed_seconds": round(run_elapsed, 3),
            "record_count": len(outputs),
        }
    )
    write_run_artifacts(args.output_dir, outputs, run_summary)
    append_event(args.output_dir, {"event": "run_done", "record_count": len(outputs), "elapsed_seconds": round(run_elapsed, 3)})
    print(f"[{now_iso()}] run_done -> {args.output_dir / 'run.json'} records={len(outputs)} elapsed={run_elapsed:.3f}s")


if __name__ == "__main__":
    main()
