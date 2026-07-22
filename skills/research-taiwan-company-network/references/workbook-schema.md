# Workbook schema

## Executive Summary

Show the resolved root entity, as-of date, research perimeter, counts by relationship class and market status, total non-duplicated recognized investment profit/loss by period, top capitalized private/public-unlisted prospects, open evidence issues, and a short legal-perimeter caveat.

## Company Universe

One row per legal entity. Minimum columns:

`Entity ID`, `Company name`, `Unified business number / jurisdiction`, `Stock code`, `Market status`, `Registry status`, `Country`, `Primary relationship class`, `Anchor company`, `Direct parent/investor`, `Ownership %`, `Representative`, `Registered capital`, `Paid-in capital`, `MOPS paid-in capital`, `Setup date`, `Latest registry change`, `Address`, `IPO potential`, `SPO/funding potential`, `Confidence`, `Source URL`, `Source locator`, `Notes`.

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
