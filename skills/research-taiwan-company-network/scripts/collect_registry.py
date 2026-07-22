#!/usr/bin/env python3
"""Resolve a Taiwan company query and collect official registry/market seed data."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


GCIS_ROOT = "https://data.gcis.nat.gov.tw/od/data/api"
COMPANY_BASIC_API = f"{GCIS_ROOT}/5F64D864-61CB-4D0D-8AD9-492047CC1EA6"
COMPANY_NAME_API = f"{GCIS_ROOT}/6BBA2268-1367-4B42-9CCA-BC17499EBE8C"
OFFICER_API = f"{GCIS_ROOT}/4E5F7653-1B91-4DDC-99D5-468530FAE396"
REPRESENTATIVE_API = f"{GCIS_ROOT}/4B61A0F1-458C-43F9-93F3-9FD6DA5E1B08"

MARKET_FILES = {
    "上市": "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv",
    "上櫃": "https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv",
    "興櫃": "https://mopsfin.twse.com.tw/opendata/t187ap03_R.csv",
    "公開發行未上市櫃": "https://mopsfin.twse.com.tw/opendata/t187ap03_P.csv",
}

ACTIVE_STATUS = "01"


class Fetcher:
    def __init__(self, allow_insecure: bool = False):
        self.context = ssl._create_unverified_context() if allow_insecure else ssl.create_default_context()
        self.allow_insecure = allow_insecure

    def bytes(self, url: str, params: dict[str, object] | None = None, attempts: int = 4) -> bytes:
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; TaiwanCompanyResearch/1.0)"},
        )
        error: Exception | None = None
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(request, timeout=60, context=self.context) as response:
                    return response.read()
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                error = exc
                time.sleep(0.6 * (attempt + 1))
        curl = shutil.which("curl")
        if curl:
            command = [
                curl,
                "-fsSL",
                "--retry",
                "3",
                "--connect-timeout",
                "20",
                "--max-time",
                "90",
                "-A",
                "Mozilla/5.0 (compatible; TaiwanCompanyResearch/1.0)",
            ]
            if self.allow_insecure:
                command.append("-k")
            command.append(url)
            completed = subprocess.run(command, capture_output=True, timeout=120, check=False)
            if completed.returncode == 0:
                return completed.stdout
            curl_error = completed.stderr.decode("utf-8", errors="replace").strip()
            error = RuntimeError(f"curl exit {completed.returncode}: {curl_error}")
        raise RuntimeError(f"Failed to fetch {url}: {error}")

    def json(self, url: str, params: dict[str, object]) -> list[dict[str, object]]:
        body = self.bytes(url, params).decode("utf-8-sig").strip()
        return json.loads(body) if body else []


def gcis(fetcher: Fetcher, api: str, filter_text: str, top: int = 1000) -> list[dict[str, object]]:
    return fetcher.json(
        api,
        {"$format": "json", "$filter": filter_text, "$skip": 0, "$top": top},
    )


def market_catalog(fetcher: Fetcher) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    warnings: list[str] = []
    for status, url in MARKET_FILES.items():
        try:
            text = fetcher.bytes(url).decode("utf-8-sig")
            for row in csv.DictReader(io.StringIO(text)):
                normalized = {str(k).strip(): str(v or "").strip() for k, v in row.items()}
                normalized["_market_status"] = status
                normalized["_source_url"] = url
                rows.append(normalized)
        except Exception as exc:  # Preserve partial official results.
            warnings.append(f"Could not load {status} catalog: {exc}")
    return rows, warnings


def market_record(row: dict[str, str]) -> dict[str, object]:
    capital = row.get("實收資本額", "").replace(",", "")
    return {
        "market_status": row.get("_market_status", ""),
        "stock_code": row.get("公司代號", ""),
        "company_name": row.get("公司名稱", ""),
        "unified_business_number": row.get("營利事業統一編號", ""),
        "paid_in_capital_twd": int(capital) if capital.isdigit() else None,
        "industry": row.get("產業別", ""),
        "listing_date": row.get("上市日期", row.get("上櫃日期", "")),
        "catalog_date": row.get("出表日期", ""),
        "source_url": row.get("_source_url", ""),
    }


def normalize_name(value: str) -> str:
    return re.sub(r"[\s　]", "", value).replace("(股)公司", "股份有限公司")


def choose_matches(query: str, catalog: list[dict[str, str]]) -> list[dict[str, object]]:
    normalized_query = normalize_name(query).lower()
    exact_ticker = [r for r in catalog if r.get("公司代號", "").lower() == query.lower()]
    if exact_ticker:
        return [market_record(r) for r in exact_ticker]
    exact_name = [r for r in catalog if normalize_name(r.get("公司名稱", "")).lower() == normalized_query]
    if exact_name:
        return [market_record(r) for r in exact_name]
    partial = [r for r in catalog if normalized_query in normalize_name(r.get("公司名稱", "")).lower()]
    return [market_record(r) for r in partial[:20]]


def resolve_company(fetcher: Fetcher, query: str, catalog: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    market_matches = choose_matches(query, catalog)
    if re.fullmatch(r"\d{8}", query):
        rows = gcis(fetcher, COMPANY_BASIC_API, f"Business_Accounting_NO eq {query}", top=50)
        return rows, market_matches

    if market_matches and any(m.get("stock_code") == query for m in market_matches):
        uid = str(market_matches[0].get("unified_business_number", ""))
        rows = gcis(fetcher, COMPANY_BASIC_API, f"Business_Accounting_NO eq {uid}", top=50) if uid else []
        return rows, market_matches

    if market_matches and len(market_matches) == 1:
        uid = str(market_matches[0].get("unified_business_number", ""))
        rows = gcis(fetcher, COMPANY_BASIC_API, f"Business_Accounting_NO eq {uid}", top=50) if uid else []
        if rows:
            return rows, market_matches

    rows = gcis(
        fetcher,
        COMPANY_NAME_API,
        f"Company_Name like {query} and Company_Status eq {ACTIVE_STATUS}",
        top=100,
    )
    return rows, market_matches


def enrich_company_market(company: dict[str, object], catalog: list[dict[str, str]]) -> dict[str, object] | None:
    uid = str(company.get("Business_Accounting_NO", ""))
    for row in catalog:
        if row.get("營利事業統一編號", "") == uid:
            return market_record(row)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve a Taiwan company name, unified business number, or stock code using official sources."
    )
    parser.add_argument("query", help="Company name, 8-digit unified business number, or stock code")
    parser.add_argument("--out", required=True, help="Absolute or relative JSON output path")
    parser.add_argument("--max-related", type=int, default=200, help="Maximum representative-related companies")
    parser.add_argument(
        "--allow-insecure",
        action="store_true",
        help="Disable TLS certificate verification only when a local proxy breaks official HTTPS certificates",
    )
    args = parser.parse_args()

    query = args.query.strip()
    fetcher = Fetcher(args.allow_insecure)
    catalog, warnings = market_catalog(fetcher)
    companies, market_matches = resolve_company(fetcher, query, catalog)

    result: dict[str, object] = {
        "query": query,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "allow_insecure_transport": args.allow_insecure,
        "resolution_status": "not_found",
        "resolution_candidates": companies,
        "market_matches": market_matches,
        "resolved_company": None,
        "resolved_market": None,
        "officers": [],
        "representative_companies": [],
        "warnings": warnings,
        "sources": {
            "company_basic_api": COMPANY_BASIC_API,
            "company_name_api": COMPANY_NAME_API,
            "officer_api": OFFICER_API,
            "representative_api": REPRESENTATIVE_API,
            "market_catalogs": MARKET_FILES,
            "findbiz": "https://findbiz.nat.gov.tw/",
        },
    }

    if len(companies) == 1:
        root = companies[0]
        uid = str(root.get("Business_Accounting_NO", ""))
        representative = str(root.get("Responsible_Name", "")).strip()
        result["resolution_status"] = "resolved"
        result["resolved_company"] = root
        result["resolved_market"] = enrich_company_market(root, catalog)
        result["officers"] = gcis(fetcher, OFFICER_API, f"Business_Accounting_NO eq {uid}", top=1000)

        if representative:
            related = gcis(
                fetcher,
                REPRESENTATIVE_API,
                f"Responsible_Name eq {representative}",
                top=min(max(args.max_related, 1), 1000),
            )
            enriched = []
            for company in related:
                enriched.append({
                    **company,
                    "market": enrich_company_market(company, catalog),
                    "relationship_class": "代表人延伸（非持股證據）",
                    "identity_status": "姓名完全相同；仍須核實",
                })
            result["representative_companies"] = enriched
    elif len(companies) > 1:
        result["resolution_status"] = "ambiguous"
        result["warnings"].append("Multiple active registry candidates matched; choose one unified business number before continuing.")
    else:
        result["warnings"].append("No active Taiwan company matched the query. Check historical status, spelling, or foreign jurisdiction.")

    output = Path(args.out).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "resolution_status": result["resolution_status"],
        "candidate_count": len(companies),
        "officer_count": len(result["officers"]),
        "representative_company_count": len(result["representative_companies"]),
        "warning_count": len(result["warnings"]),
    }, ensure_ascii=False))
    return 0 if result["resolution_status"] == "resolved" else 2


if __name__ == "__main__":
    sys.exit(main())
