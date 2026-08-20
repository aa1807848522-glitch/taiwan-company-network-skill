# Underwriting prospect screen

Read this reference whenever the workbook includes IPO, SPO, transfer-listing, or fundraising coverage. The purpose is prioritization for follow-up, not a legal conclusion, mandate claim, or investment recommendation.

## Normalize the inputs

Before scoring, normalize one Company Universe row per legal entity:

- Taiwan entity key: unified business number.
- Foreign entity key: jurisdiction plus legal name.
- Current market status: `上市`, `上櫃`, `興櫃`, `公開發行（未上市櫃）`, `未公發（依MOPS名單比對）`, or `未見於目前公開市場名單`.
- Current/historical status and evidence confidence.
- Registered capital and paid-in capital in original units.
- Relationship class, anchor company, representative, and officer-identity status when applicable.

Use `未公發（依MOPS名單比對）` only when an active Taiwan company is absent from all four current MOPS catalogs. This is a screening label tied to the catalog date, not an official certificate of non-public status.

## Effective capital

For a current Taiwan company with status `核准設立`:

1. Use current GCIS paid-in capital when it is disclosed and greater than zero.
2. Otherwise use current GCIS registered capital.
3. Store `有效資本額依據` as `實收資本額` or `登記資本額替代` and retain the source date.

Do not use MOPS capital to overwrite GCIS capital; retain both and explain differences. Do not rank inactive, historical, unresolved-homonym, or foreign entities by Taiwan effective capital.

## IPO priority screen

An entity enters the first-page IPO priority table only when all conditions are met:

- Taiwan company, current and `核准設立`;
- market status `未公發（依MOPS名單比對）`;
- confidence A or B;
- not `歷史／退出` and not `同名待核實`;
- effective capital is available;
- it is an operating company, or there is evidence that an investment/holding vehicle has an IPO-relevant operating business.

The fact that an entity has high paid-in capital is not operating evidence. Use registered business items, the issuer's official description, financial-statement operating disclosures, or an explicit normalized field such as `is_operating_company`. Treat pure investment platforms, corporate venture vehicles, nominee/custody entities, and group shareholding tools as `生態系轉介／觀察`, even when capital exceeds the IPO threshold.

Assign:

| Priority | Effective capital | First-page treatment |
|---|---:|---|
| `IPO高` | TWD 500 million or more | Include; highest priority |
| `IPO中` | TWD 100 million to below 500 million | Include |
| `IPO觀察` | TWD 50 million to below 100 million | Keep in Company Universe; omit from the priority table unless requested |
| `低於規模門檻` | Below TWD 50 million | Exclude from priority counts |

Do not elevate a pure investment company solely because of capital. Mark it `投資平台－需營運證據` unless operating-company evidence supports a higher classification.

## Public-market coverage screen

Every current in-scope company with confidence A or B and one of the following statuses belongs in the first-page public-market table:

| Market status | Coverage type | Suggested entry direction |
|---|---|---|
| `上市`, `上櫃` | `SPO／再籌資` | SPO、現增、可轉債、私募、策略股東或其他股權資本市場需求 |
| `興櫃` | `轉板／再籌資` | 上市／上櫃轉板、現增與掛牌前資本規劃 |
| `公開發行（未上市櫃）` | `掛牌／再籌資` | 興櫃／上市櫃路徑、股權結構與再籌資規劃 |

Officer-only public companies may be included only after the person link is corroborated. Their relationship text must say `代表人／董監事延伸；非集團持股證據`.

Annual-report major-shareholder paths may be included after the shareholder identity and target company are corroborated. Label the path `年報主要股東延伸；非控制證據` unless a separate ownership/control source supports a stronger relationship. Never use a custodian, nominee bank, SBL/PB account, employee omnibus account, or unidentified trading account as the target's beneficial owner.

## Required output fields

Populate these fields for every Company Universe row:

- `Effective capital`
- `Effective capital basis`
- `Underwriting coverage type`
- `Underwriting priority`
- `Initial underwriting observation`
- `Suggested entry direction`
- `Underwriting exclusion reason`

Never leave generic `未評估` text. Use an explicit exclusion such as `非台灣公司`, `未見可比較資本`, `歷史／退出`, `同名待核實排除`, `非公開市場且低於規模門檻`, or `投資平台－需營運證據`.

## Executive Summary reconciliation

- IPO table = Company Universe rows where priority is `IPO高` or `IPO中`.
- Public-market table = current Company Universe rows where coverage type is `SPO／再籌資`, `轉板／再籌資`, or `掛牌／再籌資`.
- IPO sort: `IPO高`, then `IPO中`, then effective capital descending.
- Public-market sort: `上市`, `上櫃`, `興櫃`, `公開發行（未上市櫃）`, then effective capital descending.
- Candidate counts and names must reconcile exactly. Use formulas or a deterministic pre-build screen; never maintain an independent hand-edited summary list.
- The rendered or Quick Look first page must show the reconciled values without requiring the user to trigger recalculation.
