from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field


class ReportItem(BaseModel):
    title: str
    source_url: str
    source_name: str
    companies: List[str] = Field(default_factory=list)


class Report(BaseModel):
    report_date: date
    items: List[ReportItem]
