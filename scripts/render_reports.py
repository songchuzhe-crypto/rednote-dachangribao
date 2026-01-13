from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out"
PUBLIC_DIR = ROOT / "public"
REPORTS_DIR = PUBLIC_DIR / "reports"
ASSETS_DIR = PUBLIC_DIR / "assets"


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def format_items(items: Iterable[dict]) -> str:
    rendered = []
    for item in items:
        title = item.get("title", "(untitled)")
        source_url = item.get("source_url", "#")
        source_name = item.get("source_name", "unknown")
        companies = item.get("companies") or []
        tags = "".join(
            f"<span class=\"badge\">{company}</span>" for company in companies
        )
        tags_html = f"<div class=\"tags\">{tags}</div>" if tags else ""
        rendered.append(
            "\n".join(
                [
                    "<div class=\"item\">",
                    f"  <a href=\"{source_url}\" target=\"_blank\" rel=\"noopener\">{title}</a>",
                    f"  <div class=\"meta\">{source_name}</div>",
                    f"  {tags_html}",
                    "</div>",
                ]
            )
        )
    return "\n".join(rendered)


def render_daily_page(report: dict) -> str:
    report_date = report.get("report_date", "unknown")
    items = report.get("items", [])
    items_html = format_items(items)
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"zh\">",
            "<head>",
            "  <meta charset=\"utf-8\" />",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />",
            "  <link rel=\"stylesheet\" href=\"/assets/style.css\" />",
            f"  <title>Daily Report {report_date}</title>",
            "</head>",
            "<body>",
            "  <main>",
            "    <div class=\"header\">",
            f"      <h1>{report_date} 日报</h1>",
            f"      <span class=\"meta\">条目数: {len(items)}</span>",
            "    </div>",
            items_html or "<p>暂无条目。</p>",
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def render_index_page(entries: list[tuple[str, Path]]) -> str:
    list_items = []
    for report_date, _path in entries:
        list_items.append(
            f"<li><a href=\"/reports/{report_date}/\">{report_date}</a></li>"
        )
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"zh\">",
            "<head>",
            "  <meta charset=\"utf-8\" />",
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />",
            "  <link rel=\"stylesheet\" href=\"/assets/style.css\" />",
            "  <title>Recent Reports</title>",
            "</head>",
            "<body>",
            "  <main>",
            "    <div class=\"header\">",
            "      <h1>最近 30 天日报</h1>",
            "      <span class=\"meta\">/reports/</span>",
            "    </div>",
            "    <ul class=\"listing\">",
            "      " + "\n      ".join(list_items),
            "    </ul>",
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def collect_reports(limit: int = 30) -> list[tuple[str, Path]]:
    entries = []
    if not OUT_DIR.exists():
        return entries
    for report_path in OUT_DIR.glob("*/daily.json"):
        try:
            report_date = report_path.parent.name
            datetime.strptime(report_date, "%Y-%m-%d")
        except ValueError:
            continue
        entries.append((report_date, report_path))
    entries.sort(key=lambda item: item[0], reverse=True)
    return entries[:limit]


def render_all(input_path: Path) -> None:
    report = load_report(input_path)
    report_date = report.get("report_date") or input_path.parent.name
    daily_html = render_daily_page(report)
    daily_path = REPORTS_DIR / report_date / "index.html"
    write_text(daily_path, daily_html)

    entries = collect_reports()
    index_html = render_index_page(entries)
    write_text(REPORTS_DIR / "index.html", index_html)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render report HTML pages.")
    parser.add_argument("--input", required=True, type=Path, help="Path to daily.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    render_all(args.input)


if __name__ == "__main__":
    main()
