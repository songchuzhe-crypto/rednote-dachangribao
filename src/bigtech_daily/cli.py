from __future__ import annotations

from pathlib import Path

import json
import typer

from bigtech_daily.newsbot import NewsbotClient

app = typer.Typer(add_completion=False)


@app.command()
def run(dry_run: bool = typer.Option(False, "--dry-run", help="Run without publishing.")) -> None:
    """Fetch the latest report and write a JSON payload."""
    client = NewsbotClient()
    report = client.fetch_latest_report()
    output_dir = Path("out") / report.report_date.isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "daily.json"
    payload = report.model_dump()
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(f"dry_run={dry_run}")
    typer.echo(f"report_date={report.report_date}")
    typer.echo(f"items={len(report.items)}")
    typer.echo(f"output_path={output_path}")


if __name__ == "__main__":
    app()
