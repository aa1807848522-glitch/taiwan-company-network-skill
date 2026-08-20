# Primary data sources and search order

## Taiwan registry

Use the Ministry of Economic Affairs, Administration of Commerce sources first.

| Purpose | Official source |
|---|---|
| Company basic data by unified business number | `https://data.gcis.nat.gov.tw/od/data/api/5F64D864-61CB-4D0D-8AD9-492047CC1EA6` |
| Company-name keyword search | `https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C` |
| Directors and supervisors by unified business number | `https://data.gcis.nat.gov.tw/od/data/api/4E5F7653-1B91-4DDC-99D5-468530FAE396` |
| Companies by registered representative name | `https://data.gcis.nat.gov.tw/od/data/api/4B61A0F1-458C-43F9-93F3-9FD6DA5E1B08` |
| National monthly directors/supervisors dataset | `https://data.gov.tw/dataset/96731` |
| Human-readable company page and final verification | `https://findbiz.nat.gov.tw/` |
| GCIS API guide | `https://data.gcis.nat.gov.tw/od/rule` |

The per-company officer API returns current office title, person name, represented legal person, and shares. Use the monthly national dataset to reverse-match a person into other companies. Because exact Chinese names are not unique identifiers, do not treat a reverse match as identity proof without corroboration.

## Capital-market identity

Download the current company catalogs and map by unified business number first, stock code second.

| Status | Source |
|---|---|
| Listed | `https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv` |
| OTC | `https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv` |
| Emerging | `https://mopsfin.twse.com.tw/opendata/t187ap03_R.csv` |
| Public but not listed/OTC | `https://mopsfin.twse.com.tw/opendata/t187ap03_P.csv` |

For a Taiwan company whose current registry status is `核准設立`, absence by unified business number from all four current catalogs may be labeled `未公發（依MOPS名單比對）` for underwriting screening, with the catalog date recorded. This is a dated screening label, not an official non-public certificate. When the registry is inactive, the entity is foreign, or identity is unresolved, use `未見於目前公開市場名單` unless stronger current evidence supports a more specific status.

## Ownership, subsidiaries, and investments

Search in this order:

1. Latest consolidated annual report: organization chart, subsidiaries, related parties, investments accounted for using equity method, FVOCI/FVTPL holdings, major shareholders, and changes in the group.
2. Latest quarterly consolidated financial statements: updated investment scope and recognized investment profit or loss.
3. MOPS financial comparison / investment note `SubsidiaryInfo`.
4. Material information, board resolutions, private placements, capital increases, merger or disposal announcements.
5. Investee's own filings and official website.
6. Registry legal-person directors and current officers.

MOPS root: `https://mopsfin.twse.com.tw/`

The comparison endpoint currently uses a POST to `/compare/xb` with `compareItem=SubsidiaryInfo`, a reporting period code, and `companyId`. Treat the endpoint as unstable UI plumbing: if it changes, use the annual report or financial-statement note directly rather than fabricating an empty result.

## Foreign entities

Use the parent company's filed financial statements as the minimum evidence. If capital, status, or officers are material, verify with the foreign jurisdiction's official registry. Preserve original currency and reporting date; add a translated TWD amount only when the user asks, with the exchange-rate source and date.

## Search and citation discipline

- Use web search to locate filings, then open the primary document.
- Cite the direct page or PDF, not a search-results page.
- Record document title, issuer, period, publication date, retrieval date, and page/table locator.
- Keep short extracts only; summarize rather than copying filings.
- If no public source discloses a private holding percentage or investment result, write `未公開揭露`, not `0`.
