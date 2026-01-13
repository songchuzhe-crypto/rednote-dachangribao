#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="${ROOT_DIR}/src"
python -m bigtech_daily run

REPORT_DATE=$(python - <<'PY'
from datetime import datetime, timedelta, timezone

jst = timezone(timedelta(hours=9))
print(datetime.now(tz=jst).date().isoformat())
PY
)

python scripts/render_reports.py --input "out/${REPORT_DATE}/daily.json"

echo "Rendered public/reports/${REPORT_DATE}/index.html"
echo "Rendered public/reports/index.html"
