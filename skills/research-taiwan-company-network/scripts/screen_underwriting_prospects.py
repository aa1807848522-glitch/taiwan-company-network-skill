#!/usr/bin/env python3
"""Apply the skill's deterministic IPO and public-market coverage screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PUBLIC_MARKETS = {
    "上市": ("SPO／再籌資", "公開市場覆蓋", "SPO、現增、可轉債、私募、策略股東或其他股權資本市場需求", 0),
    "上櫃": ("SPO／再籌資", "公開市場覆蓋", "SPO、現增、可轉債、私募、策略股東或其他股權資本市場需求", 1),
    "興櫃": ("轉板／再籌資", "轉板優先", "上市／上櫃轉板、現增與掛牌前資本規劃", 2),
    "公開發行（未上市櫃）": ("掛牌／再籌資", "掛牌路徑", "興櫃／上市櫃路徑、股權結構與再籌資規劃", 3),
}
PRIVATE_MARKETS = {"未公發（依MOPS名單比對）", "未公發／未上市櫃", "未公發"}
HISTORICAL_TERMS = ("歷史", "退出", "清算", "解散", "撤銷", "廢止", "合併消滅")
INVESTMENT_VEHICLE_TERMS = ("投資", "控股", "資產管理", "創投", "capital", "holding")


def first(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def twd_amount(value: Any, unit: Any) -> float | None:
    amount = number(value)
    if amount is None:
        return None
    normalized = str(unit or "TWD").lower().replace(" ", "")
    if any(token in normalized for token in ("usd", "rmb", "cny", "jpy", "eur")):
        return None
    if "thousand" in normalized or "仟" in normalized or "千元" in normalized:
        return amount * 1000
    return amount


def is_true(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"1", "true", "yes", "y", "是"}


def is_taiwan(country: Any) -> bool:
    return str(country or "").strip().lower() in {"台灣", "臺灣", "taiwan", "tw"}


def is_historical(row: dict[str, Any]) -> bool:
    text = " ".join(
        str(first(row, key, default=""))
        for key in ("current_historical", "status", "relationship_class", "primary_relationship_class", "registry_status")
    ).lower()
    return any(term.lower() in text for term in HISTORICAL_TERMS)


def has_operating_evidence(row: dict[str, Any], name: str) -> bool:
    if is_true(first(row, "operating_company_evidence", "is_operating_company", default=False)):
        return True
    lowered = name.lower()
    return not any(term in lowered for term in INVESTMENT_VEHICLE_TERMS)


def effective_capital(row: dict[str, Any]) -> tuple[float | None, str]:
    country = first(row, "country", "Country")
    registry_status = str(first(row, "registry_status", "Registry status", default=""))
    if not is_taiwan(country) or "核准設立" not in registry_status or is_historical(row):
        return None, ""

    paid = twd_amount(
        first(row, "paid_in_capital", "Paid-in capital"),
        first(row, "paid_in_capital_unit", "Paid-in capital currency/unit", "capital_unit", default="TWD"),
    )
    if paid is not None and paid > 0:
        return paid, "實收資本額"

    registered = twd_amount(
        first(row, "registered_capital", "Registered capital"),
        first(row, "registered_capital_unit", "capital_unit", default="TWD"),
    )
    if registered is not None and registered > 0:
        return registered, "登記資本額替代"
    return None, ""


def screen_row(raw: dict[str, Any]) -> dict[str, Any]:
    row = dict(raw)
    name = str(first(row, "company_name", "name", "Company name", default="未命名公司"))
    market = str(first(row, "market_status", "Market status", default=""))
    registry = str(first(row, "registry_status", "Registry status", default=""))
    country = first(row, "country", "Country")
    relationship = str(first(row, "relationship_class", "primary_relationship_class", "Primary relationship class", default=""))
    confidence = str(first(row, "confidence", "Confidence", default="")).upper()
    identity = str(first(row, "identity_status", "Identity status", default=""))
    capital, capital_basis = effective_capital(row)

    coverage_type = "不列入優先覆蓋"
    priority = ""
    direction = ""
    observation = ""
    exclusion = ""

    if identity == "同名待核實" or confidence not in {"A", "B"}:
        exclusion = "同名待核實排除" if identity == "同名待核實" else "證據信心不足"
    elif is_historical(row):
        exclusion = "歷史／退出"
    elif market in PUBLIC_MARKETS:
        coverage_type, priority, direction, _ = PUBLIC_MARKETS[market]
        relation_text = relationship or "公司網絡內公開市場公司"
        if "代表人／董監事" in relation_text:
            relation_text = "代表人／董監事延伸；非集團持股證據"
        observation = f"{market}公司；{relation_text}"
    elif not is_taiwan(country):
        exclusion = "非台灣公司"
    elif "核准設立" not in registry:
        exclusion = "非現行核准設立公司"
    elif market not in PRIVATE_MARKETS:
        exclusion = "市場身分資料不足"
    elif capital is None:
        exclusion = "未見可比較資本"
    elif not has_operating_evidence(row, name):
        exclusion = "投資平台－需營運證據"
        priority = "IPO觀察"
    else:
        coverage_type = "IPO候選"
        if capital >= 500_000_000:
            priority = "IPO高"
            observation = "未公發且核准設立；有效資本額達5億元，列優先覆蓋"
        elif capital >= 100_000_000:
            priority = "IPO中"
            observation = "未公發且核准設立；有效資本額達1億元，適合持續追蹤"
        elif capital >= 50_000_000:
            priority = "IPO觀察"
            observation = "未公發且核准設立；有效資本額達5,000萬元，保留觀察"
        else:
            coverage_type = "不列入優先覆蓋"
            priority = "低於規模門檻"
            exclusion = "非公開市場且低於規模門檻"

    row.update(
        {
            "effective_capital": capital,
            "effective_capital_basis": capital_basis,
            "underwriting_coverage_type": coverage_type,
            "underwriting_priority": priority,
            "initial_underwriting_observation": observation,
            "suggested_entry_direction": direction,
            "underwriting_exclusion_reason": exclusion,
        }
    )
    return row


def sort_capital(row: dict[str, Any]) -> float:
    return number(row.get("effective_capital")) or 0


def screen(rows: list[dict[str, Any]]) -> dict[str, Any]:
    enriched = [screen_row(row) for row in rows]
    ipo_rank = {"IPO高": 0, "IPO中": 1}
    ipo = [row for row in enriched if row["underwriting_priority"] in ipo_rank]
    ipo.sort(key=lambda row: (ipo_rank[row["underwriting_priority"]], -sort_capital(row), str(first(row, "company_name", "name", "Company name", default=""))))

    watch = [row for row in enriched if row["underwriting_priority"] == "IPO觀察"]
    watch.sort(key=lambda row: (-sort_capital(row), str(first(row, "company_name", "name", "Company name", default=""))))

    market_rank = {market: details[3] for market, details in PUBLIC_MARKETS.items()}
    public = [row for row in enriched if str(first(row, "market_status", "Market status", default="")) in PUBLIC_MARKETS and row["underwriting_coverage_type"] != "不列入優先覆蓋"]
    public.sort(key=lambda row: (market_rank[str(first(row, "market_status", "Market status"))], -sort_capital(row), str(first(row, "company_name", "name", "Company name", default=""))))

    return {
        "thresholds_twd": {"ipo_high": 500_000_000, "ipo_medium": 100_000_000, "ipo_watch": 50_000_000},
        "ipo_candidates": ipo,
        "ipo_watchlist": watch,
        "public_market_candidates": public,
        "enriched_companies": enriched,
        "reconciliation": {
            "ipo_candidate_count": len(ipo),
            "public_market_candidate_count": len(public),
            "ipo_candidate_names": [str(first(row, "company_name", "name", "Company name", default="")) for row in ipo],
            "public_market_candidate_names": [str(first(row, "company_name", "name", "Company name", default="")) for row in public],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON list or object containing a companies list")
    parser.add_argument("--out", type=Path, help="Output JSON path; stdout when omitted")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    rows = payload.get("companies") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        parser.error("input must be a JSON list of company objects or an object with a companies list")

    output = json.dumps(screen(rows), ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
