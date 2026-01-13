from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def jst_today() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(tz=jst).date().isoformat()


def run_command() -> Path:
    report_date = jst_today()
    output_dir = Path("out") / report_date
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "daily.json"
    payload = {
        "report_date": report_date,
        "items": [],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bigtech_daily")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run", help="Generate daily.json placeholder.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "run":
        output_path = run_command()
        print(f"daily_json={output_path}")


if __name__ == "__main__":
    main()
