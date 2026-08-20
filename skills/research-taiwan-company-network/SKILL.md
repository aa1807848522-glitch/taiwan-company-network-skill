---
name: research-taiwan-company-network
description: Research a Taiwan company from a company name, 8-digit unified business number (統編), or listed/OTC/emerging stock code, then deliver a source-backed Excel workbook covering the legal ownership perimeter, investees and investment P&L, annual-report major shareholders, officer and strategic-shareholder networks, second-tier subsidiaries, registry and public-market status, and actionable IPO/SPO customer-development paths. Use for company-group mapping, investment-banking prospecting, IPO/SPO lead screening, 關係企業整理, 轉投資事業群分析, 年報主要股東延伸, 商工登記董監事延伸, or replacing an XMind company chart with a structured research document.
---

# Taiwan Company Network Research

## Goal

Turn one Taiwan company identifier into an auditable company-network workbook. Default to `.xlsx`; produce `.docx` only when the user explicitly asks for a narrative report. Never create an XMind file unless explicitly requested.

Unless the user explicitly opts out of underwriting prospecting, make the first worksheet an actionable coverage page. It must name the qualifying IPO candidates and the public-market SPO／轉板／再籌資 targets; prospect fields may not be left as generic `未評估` placeholders when the available registry and market data are sufficient to classify them.

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

Follow every newly found material entity one level further. Continue until a pass produces no new material controlled entity, or the user-specified depth is reached. Default depth is three legal ownership levels plus two commercial-expansion levels: current officers and annual-report major shareholders, followed by one level of their verified operating companies or investment portfolios.

### 2. Capture investments and earnings

For every disclosed investment edge, capture investor, investee, direct ownership percentage, shares, original investment amount, carrying amount, investee period profit or loss, recognized investment profit or loss, period, unit, accounting classification, and source locator.

Use MOPS financial-comparison item `SubsidiaryInfo` when available, then reconcile it to the financial-statement note. Keep blank values blank; blank does not mean zero. Do not sum a parent's recognized investment result together with the same result again at a lower-tier reporting company. Mark which rows enter the non-duplicated summary.

### 3. Expand the officer network

Use the GCIS officer API to obtain current directors, supervisors, and legal-person representatives for each in-scope Taiwan company. Then expand:

- companies for which the root representative is also the registered representative;
- other companies where the root representative serves as director or supervisor;
- other current companies of every material director, independent director, supervisor, legal-person representative, CEO, CFO, or other named executive of the root and each material listed investee;
- the next-level subsidiaries or operating investees of a material listed associate when its annual report makes them visible.

Prefer the official monthly national officer dataset for reverse-name matching. Exact-name matches are candidates, not identity proof. Confirm material matches against the current FindBiz company page and, when possible, corroborate with the same legal-person employer, address, filing, biography, or another primary source. Label unresolved homonyms `同名待核實` and exclude them from group ownership counts.

### 4. Expand annual-report major shareholders

For the root and each material listed associate, extract the latest annual-report major-shareholder or top-ten-shareholder table. Treat it as a separate expansion axis from officer roles:

- verify Taiwan corporate shareholders by unified business number and current GCIS/MOPS status;
- follow a corporate shareholder to its disclosed parent, legal-person representative, current directors, and one level of verified operating companies or investment portfolio;
- follow a natural-person shareholder only when the annual report or another primary source clearly ties that person to current company roles; do not run broad same-name searches;
- preserve disclosed ownership percentages and as-of dates;
- exclude nominee banks, custody accounts, SBL/PB accounts, omnibus employee accounts, and unidentified trading accounts from beneficial-owner inference;
- merge duplicate target companies while retaining every distinct shareholder, officer, investment, or governance path in the relationship map.

Use `年報主要股東延伸（非控制證據）` as the relationship label unless a separate source proves control. A major shareholder is a customer-development route, not automatically the root company's parent or related party.

### 5. Classify each relationship

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

Add `年報主要股東延伸（非控制證據）` as a secondary tag when relevant. Keep multiple relationship edges even though `Company Universe` has only one row per legal entity.

Never infer parent-subsidiary status from a shared surname, shared officer, group branding, office address, or the word “關係企業” alone.

### 6. Determine company and market status

For Taiwan entities, record GCIS registration status, registered capital, paid-in capital, representative, address, setup date, and latest registry change. Determine capital-market status from current MOPS/TWSE open data using this precedence:

`上市` → `上櫃` → `興櫃` → `公開發行（未上市櫃）` → `未公發（依MOPS名單比對）`.

Use `未公發（依MOPS名單比對）` only for a Taiwan company whose current registry status is `核准設立` and whose unified business number is absent from all four current MOPS market catalogs. For inactive Taiwan entities and foreign entities, use `未見於目前公開市場名單` unless stronger evidence supports a more specific status. If a company is dissolved, revoked, merged, liquidated, or historical, preserve that status even if an old market code exists. Reconcile capital differences between GCIS and MOPS by retaining both values and their dates rather than silently choosing one.

### 7. Apply banking prospecting fields

Unless the user explicitly asks for legal-network research only, read `references/underwriting-screen.md` and apply it after the Company Universe is stable. Run `scripts/screen_underwriting_prospects.py` when the entity data can be normalized to JSON; otherwise apply the same rules directly and document any deviation.

The screen must:

- derive an auditable `有效資本額` from current Taiwan registry data;
- assign an explicit coverage type, priority, rationale, and suggested entry direction;
- exclude inactive or historical entities, foreign entities without comparable Taiwan capital evidence, and unresolved homonyms from IPO priority counts;
- retain verified officer-only prospects but label the relationship as non-ownership evidence;
- reconcile the candidate counts and names shown on `Executive Summary` to the detailed rows in `Company Universe`;
- exclude pure investment, custody, nominee, and non-operating platform entities from IPO high/medium solely on capital, while retaining them as portfolio-introduction routes;
- distinguish direct ownership, officer/governance links, annual-report shareholder links, and strategic-shareholder links in the commercial relationship path.

These are preliminary coverage judgments, not verified mandates or recommendations. If evidence is insufficient, use a specific result such as `資料不足`, `低於規模門檻`, `歷史／退出`, or `同名待核實排除` instead of `未評估`.

## Build the workbook

Use the `spreadsheets:Spreadsheets` skill to create and verify the `.xlsx`. Follow `references/workbook-schema.md`. The workbook must contain:

- `Executive Summary`
- `Company Universe`
- `Relationship & Coverage Map`
- `Ownership & Investments`
- `Investment P&L`
- `Officer Network`
- `Major Shareholder Expansion`
- `Sources & Definitions`
- `Source Trace`

Make all detail ranges filterable tables. Freeze headers, wrap long text, format TWD and TWD-thousand columns explicitly, and use conditional formatting for market status, inactive companies, and unresolved evidence. Include clickable source URLs and source locators in the workbook. Do not rely on cell color as the only carrier of meaning. Every detail sheet must use the same researched perimeter; do not leave the relationship map, shareholder expansion, P&L, officer network, or trace sheets at a narrower root-only scope after `Company Universe` has been expanded.

The first worksheet is a coverage dashboard, not only a research summary. It must visibly contain, in this order:

1. an executive snapshot;
2. `IPO候選：未公發且具規模之優先覆蓋公司` with qualifying company names, effective capital, representative, relationship anchor, priority, rationale, and registry status;
3. `SPO／轉板／再籌資覆蓋：已公開市場公司` with company name, stock code, market status, effective capital, network relationship, suggested entry direction, representative, and notes;
4. next-step coverage actions and evidence gaps.

Sort IPO candidates by `IPO高` before `IPO中`, then effective capital descending. Sort public-market coverage by market path and effective capital descending. When a section has no qualifying company, show one explicit `本次未發現符合條件者` row rather than omitting the section.

The first page must remain readable in file previews that do not recalculate formulas. Use deterministic as-of values for the snapshot and candidate tables, or ensure formula caches contain the same values. Never deliver a first page that previews as zero or blank while the detail sheets contain candidates.

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
- Effective capital basis is explicit and uses consistent TWD units.
- Every eligible company has a non-placeholder underwriting classification or a documented exclusion reason.
- Executive Summary visibly lists IPO high/medium candidates and all current public-market coverage companies.
- Executive Summary candidate counts and names reconcile to Company Universe.
- Investment P&L includes period and unit and avoids double counting.
- Historical and inactive entities are visible, not deleted.
- Material officer matches are confirmed or labeled as homonyms.
- Latest annual-report major shareholders are extracted for the root and material listed associates, with custody/nominee accounts explicitly excluded from beneficial-owner expansion.
- Corporate and identity-verified natural-person shareholders are expanded one level, with duplicate companies merged but all distinct paths retained.
- Relationship & Coverage Map contains the commercial introduction path, evidence type, boundary, suggested product, and next action for every priority IPO/public-market target.
- Major Shareholder Expansion and Source Trace reconcile to the latest annual-report tables and Company Universe.
- Every material row has at least one source and confidence label.
- Workbook opens cleanly and has no formula errors.
