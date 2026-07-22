---
name: research-taiwan-company-network
description: Research a Taiwan company from a company name, 8-digit unified business number (統編), or listed/OTC/emerging stock code, then deliver a source-backed Excel workbook covering the legal parent-subsidiary hierarchy, investees and investments, recognized investment profit or loss, registry capital and status, public-market status, representatives/directors/supervisors, and the representative's or officers' other registered companies. Use for company-group mapping, investment-banking prospecting, IPO/SPO lead screening, 關係企業整理, 轉投資事業群分析, 商工登記董監事延伸, or replacing an XMind company chart with a structured research document.
---

# Taiwan Company Network Research

## Goal

Turn one Taiwan company identifier into an auditable company-network workbook. Default to `.xlsx`; produce `.docx` only when the user explicitly asks for a narrative report. Never create an XMind file unless explicitly requested.

Separate legally evidenced ownership or control from officer-only associations. Treat completeness as a documented research scope, not a claim that every private investment is publicly observable.

## Start

1. Record the user's input verbatim and the research as-of date.
2. Run `scripts/collect_registry.py` with the company name, unified business number, or stock code. It resolves the root entity and collects registry basics, market identity, current officers, and companies sharing the same registered representative.
3. If the input is ambiguous, present the top matches with name, unified business number, representative, capital, and status, then ask the user to choose. Do not research multiple homonymous entities as one company.
4. Use the resolved unified business number as the Taiwan entity key. Use jurisdiction plus legal name for foreign entities.

Example:

```bash
python3 scripts/collect_registry.py '3707' --out /absolute/output/root_registry.json
```

If the environment rejects the official site's certificate because of a local proxy, retry only the official GCIS endpoints with `--allow-insecure` and note that transport exception in the source log.

## Research workflow

### 1. Establish the legal perimeter

Find and verify:

- direct and ultimate parent, if disclosed;
- consolidated subsidiaries and sub-subsidiaries;
- associates and joint ventures accounted for using the equity method;
- non-controlling financial investments disclosed at FVOCI/FVTPL or as strategic holdings;
- branches and overseas entities;
- disposed, liquidated, dissolved, merged, or historical investments when material.

For public companies, begin with the latest annual report, latest quarterly financial statements, MOPS investment-note tables, and material announcements. For private roots, also inspect the official company website, public filings of known investees, and registry officer/legal-person links.

Follow every newly found material entity one level further. Continue until a pass produces no new material controlled entity, or the user-specified depth is reached. Default depth is three legal ownership levels plus one officer-association level.

### 2. Capture investments and earnings

For every disclosed investment edge, capture investor, investee, direct ownership percentage, shares, original investment amount, carrying amount, investee period profit or loss, recognized investment profit or loss, period, unit, accounting classification, and source locator.

Use MOPS financial-comparison item `SubsidiaryInfo` when available, then reconcile it to the financial-statement note. Keep blank values blank; blank does not mean zero. Do not sum a parent's recognized investment result together with the same result again at a lower-tier reporting company. Mark which rows enter the non-duplicated summary.

### 3. Expand the officer network

Use the GCIS officer API to obtain current directors, supervisors, and legal-person representatives for each in-scope Taiwan company. Then expand:

- companies for which the root representative is also the registered representative;
- other companies where the root representative serves as director or supervisor;
- optionally, other companies of additional directors/supervisors when the user requests a broader network or the connection is material.

Prefer the official monthly national officer dataset for reverse-name matching. Exact-name matches are candidates, not identity proof. Confirm material matches against the current FindBiz company page and, when possible, corroborate with the same legal-person employer, address, filing, biography, or another primary source. Label unresolved homonyms `同名待核實` and exclude them from group ownership counts.

### 4. Classify each relationship

Use exactly one primary relationship class and optional secondary tags:

1. `法定母公司／控制股東`
2. `合併子公司`
3. `關聯企業／合資（權益法）`
4. `非控制性轉投資`
5. `平行關係投資平台`
6. `代表人／董監事延伸（非持股證據）`
7. `外部策略股東`
8. `歷史／退出`
9. `待核實`

Never infer parent-subsidiary status from a shared surname, shared officer, group branding, office address, or the word “關係企業” alone.

### 5. Determine company and market status

For Taiwan entities, record GCIS registration status, registered capital, paid-in capital, representative, address, setup date, and latest registry change. Determine capital-market status from current MOPS/TWSE open data using this precedence:

`上市` → `上櫃` → `興櫃` → `公開發行未上市櫃` → `未公發／未上市櫃`.

If a company is dissolved, revoked, merged, liquidated, or historical, preserve that status even if an old market code exists. Reconcile capital differences between GCIS and MOPS by retaining both values and their dates rather than silently choosing one.

### 6. Apply banking prospecting fields

When the purpose includes underwriting prospects, add separate preliminary fields for `IPO潛力` and `SPO／籌資潛力`. Base them on observable indicators such as market status, paid-in capital, growth funding, recent capital increases, public-company maturity, strategic investors, and disclosed expansion. Label these as screening judgments, not verified mandates or recommendations.

## Build the workbook

Use the `spreadsheets:Spreadsheets` skill to create and verify the `.xlsx`. Follow `references/workbook-schema.md`. The workbook must contain:

- `Executive Summary`
- `Company Universe`
- `Ownership & Investments`
- `Investment P&L`
- `Officer Network`
- `Sources & Definitions`

Make all detail ranges filterable tables. Freeze headers, wrap long text, format TWD and TWD-thousand columns explicitly, and use conditional formatting for market status, inactive companies, and unresolved evidence. Include clickable source URLs and source locators in the workbook. Do not rely on cell color as the only carrier of meaning.

Before delivery, verify formulas, row counts, duplicate unified business numbers, ownership percentages, period units, and source coverage. Render or inspect the workbook visually according to the spreadsheet skill. Deliver only the final workbook and concise caveats; keep intermediate JSON and downloads in a supporting-data subfolder.

## Evidence rules

Read `references/data-sources.md` before browsing. Prefer primary sources and cite the exact filing or official registry page. For every material claim, store source URL, document date or period, retrieval date, and page/table/row locator.

Use these confidence labels:

- `A`: current official registry or filed financial statement directly supports the field;
- `B`: issuer website or official announcement supports it, but the legal or accounting perimeter is not fully shown;
- `C`: officer-name match or credible secondary source that still needs primary confirmation;
- `D`: inference only; exclude from ownership totals.

If evidence conflicts, preserve both observations, explain the date or scope difference, and flag the row for review. Do not overwrite a current registry fact with an older annual-report fact.

## Completion checklist

- Root entity uniquely resolved.
- Every Taiwan entity has a unified business number or a reason it could not be found.
- Every entity has a primary relationship class and anchor company.
- Ownership and officer-only associations are separated.
- Public-market status is current as of the research date.
- Capital source and date are recorded.
- Investment P&L includes period and unit and avoids double counting.
- Historical and inactive entities are visible, not deleted.
- Material officer matches are confirmed or labeled as homonyms.
- Every material row has at least one source and confidence label.
- Workbook opens cleanly and has no formula errors.
