from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Iterable, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from bigtech_daily.schema import Report, ReportItem

REPORTS_INDEX_URL = "https://newsbot.justinyan.app/reports"
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")
COMPANY_WHITELIST = [
    "腾讯",
    "阿里",
    "字节",
    "百度",
    "京东",
    "美团",
    "拼多多",
    "网易",
    "快手",
    "小米",
    "滴滴",
    "携程",
    "哔哩哔哩",
]


@dataclass(frozen=True)
class ReportLink:
    report_date: date
    url: str


class NewsbotClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "bigtech-daily/0.1 (+https://newsbot.justinyan.app)",
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    def fetch(self, url: str) -> str:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.text

    def fetch_latest_report(self) -> Report:
        index_html = self.fetch(REPORTS_INDEX_URL)
        latest = find_latest_report_link(index_html)
        report_html = self.fetch(latest.url)
        items = parse_report_items(report_html)
        return Report(report_date=latest.report_date, items=items)


def find_latest_report_link(index_html: str) -> ReportLink:
    soup = BeautifulSoup(index_html, "lxml")
    links: List[ReportLink] = []
    for anchor in soup.find_all("a", href=True):
        text = " ".join(anchor.stripped_strings)
        href = anchor["href"]
        match = DATE_PATTERN.search(text) or DATE_PATTERN.search(href)
        if not match:
            continue
        report_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        url = urljoin(REPORTS_INDEX_URL, href)
        links.append(ReportLink(report_date=report_date, url=url))
    if not links:
        raise ValueError("No report links found on reports index page.")
    links.sort(key=lambda item: item.report_date, reverse=True)
    return links[0]


def parse_report_items(report_html: str) -> List[ReportItem]:
    soup = BeautifulSoup(report_html, "lxml")
    main = soup.find("main") or soup.find("article") or soup
    items: List[ReportItem] = []
    for li in main.find_all(["li", "div", "article"]):
        link = li.find("a", href=True)
        if not link:
            continue
        href = link["href"].strip()
        if not href.startswith("http"):
            continue
        title = " ".join(link.stripped_strings)
        if not title:
            continue
        source_name = extract_source_name(li, href)
        companies = match_companies(title)
        items.append(
            ReportItem(
                title=title,
                source_url=href,
                source_name=source_name,
                companies=companies,
            )
        )
    if not items:
        items.extend(parse_links_as_items(main))
    return dedupe_items(items)


def extract_source_name(container, href: str) -> str:
    source_tag = container.find(class_=re.compile(r"source|media", re.I))
    if source_tag:
        source_text = " ".join(source_tag.stripped_strings)
        if source_text:
            return source_text
    small = container.find("small")
    if small:
        small_text = " ".join(small.stripped_strings)
        if small_text:
            return small_text
    host = urlparse(href).netloc
    return host.replace("www.", "") if host else "unknown"


def parse_links_as_items(scope) -> List[ReportItem]:
    items: List[ReportItem] = []
    for link in scope.find_all("a", href=True):
        href = link["href"].strip()
        if not href.startswith("http"):
            continue
        title = " ".join(link.stripped_strings)
        if not title:
            continue
        items.append(
            ReportItem(
                title=title,
                source_url=href,
                source_name=urlparse(href).netloc.replace("www.", ""),
                companies=match_companies(title),
            )
        )
    return items


def match_companies(text: str) -> List[str]:
    matched = [name for name in COMPANY_WHITELIST if name in text]
    return matched


def dedupe_items(items: Iterable[ReportItem]) -> List[ReportItem]:
    seen: set[tuple[str, str]] = set()
    deduped: List[ReportItem] = []
    for item in items:
        key = (item.title, item.source_url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
