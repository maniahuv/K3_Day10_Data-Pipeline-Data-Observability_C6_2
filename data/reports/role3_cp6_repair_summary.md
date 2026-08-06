# CP6 Role 3 Repair Summary

- Repair source: `data/raw/crossref_records.json`
- Raw records: 24
- Repaired data is rebuilt from raw records; no baseline rows are copied or edited by hand.

| State | Rows | Duplicate paper IDs | Empty embedding text | `age_days` range | Quality |
| --- | ---: | ---: | ---: | --- | --- |
| Clean baseline | 22 | 0 | 0 | 5–175 | PASSED |
| Corrupted | 21 | 1 | 0 | 27–402 | WARNING |
| Repaired | 22 | 0 | 0 | 5–175 | PASSED |

The repaired schema matches the clean contract, and all repaired core fields match the clean baseline. Cleaning excluded two raw records with invalid published dates, as recorded in `data/quality/repaired_cleaning_log.json`.
