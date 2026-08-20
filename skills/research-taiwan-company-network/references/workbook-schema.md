# Workbook schema

## Executive Summary

This is the underwriting coverage page. Use a clear eight-column layout when practical and show:

1. Title, as-of date, one-sentence conclusion, and a short legal-perimeter caveat.
2. Executive snapshot: total entities, active Taiwan companies, current public-market companies, current non-public Taiwan companies, effective-capital total, non-duplicated investment P&L, and IPO high/medium count.
3. `IPO候選：未公發且具規模之優先覆蓋公司` with columns `公司`, `分類／錨點`, `有效資本額`, `代表人`, `關係人／關係依據`, `優先級`, `初步承銷觀察`, `公司狀態`.
4. `SPO／轉板／再籌資覆蓋：已公開市場公司` with columns `公司`, `代號`, `市場狀態`, `有效資本額`, `與根公司網絡關係`, `可能切入方向`, `代表人`, `備註`.
5. Three prioritized coverage actions, open evidence gaps, and worksheet navigation.

IPO rows must include only `IPO高` and `IPO中`. Public-market rows must include every current `上市`, `上櫃`, `興櫃`, or `公開發行（未上市櫃）` entity that is in scope with confidence A or B. Reconcile names and counts to `Company Universe`; do not manually curate a conflicting summary list. If a section is empty, retain its header and show `本次未發現符合條件者`.

## Company Universe

One row per legal entity. Minimum columns:

`Entity ID`, `Company name`, `Unified business number / jurisdiction`, `Stock code`, `Market status`, `Registry status`, `Country`, `Primary relationship class`, `Anchor company`, `Direct parent/investor`, `Ownership %`, `Representative`, `Registered capital`, `Paid-in capital`, `MOPS paid-in capital`, `Effective capital`, `Effective capital basis`, `Setup date`, `Latest registry change`, `Address`, `Underwriting coverage type`, `Underwriting priority`, `Initial underwriting observation`, `Suggested entry direction`, `Underwriting exclusion reason`, `Confidence`, `Source URL`, `Source locator`, `Notes`.

For current Taiwan companies, effective capital is current paid-in capital when available and positive, otherwise current registered capital. Keep the original fields and dates; `Effective capital` is a screening helper, not a replacement for legal capital disclosures. Do not create a comparable TWD effective-capital number for foreign entities without a reliable currency conversion explicitly requested by the user.

In underwriting mode, include verified officer-extension companies as Company Universe rows so they can participate in IPO/SPO screening. Keep unresolved exact-name matches in `Officer Network` only unless another primary source corroborates identity. Officer-only rows must state that the connection is not ownership evidence.

Deduplicate Taiwan companies by unified business number. Keep multiple relationship edges in `Ownership & Investments`, not duplicate company rows.

## Ownership & Investments

One row per directed relationship and period when applicable:

`Investor`, `Investee`, `Relationship class`, `Accounting classification`, `Control status`, `Ownership %`, `Shares`, `Original investment amount`, `Carrying amount`, `Effective date`, `End date`, `Current/historical`, `Evidence confidence`, `Source URL`, `Source locator`, `Notes`.

## Investment P&L

One row per reporting company, investor, investee, and reporting period:

`Period`, `Reporting company`, `Investor`, `Investee`, `Location`, `Business`, `Ownership %`, `Carrying amount (TWD thousand)`, `Investee profit/loss (TWD thousand)`, `Recognized investment profit/loss (TWD thousand)`, `Include in non-duplicated summary`, `Source URL`, `Source locator`, `Notes`.

Use a Boolean field for non-duplicated inclusion. Never infer missing amounts as zero.

## Officer Network

One row per person-company role:

`Person`, `Identity status`, `Anchor company`, `Related company`, `Unified business number`, `Role`, `Represented legal person`, `Shares`, `Company market status`, `Company registry status`, `Paid-in capital`, `Relationship class`, `Same-person evidence`, `Confidence`, `Source URL`, `Checked date`, `Notes`.

Use `Identity status` values `已核實`, `同名待核實`, or `非同一人`. Officer links are never ownership links unless a separate ownership source exists.

## Sources & Definitions

Include:

- source inventory with URL, issuer, document title, period/date, retrieval date, and pages/tables used;
- relationship-class definitions;
- confidence definitions;
- capital-market status precedence;
- accounting units and currency rules;
- research limitations and unresolved items.
