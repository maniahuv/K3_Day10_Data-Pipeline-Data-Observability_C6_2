# Corrupted Dataset Quality and RAG Impact Report

This report is separate from the baseline report and uses the corrupted dataset artifacts.

## Inputs
- Baseline metrics samples: 30
- Corrupted metrics samples: 30
- Corrupted quality status: `WARNING`
- Corrupted freshness status: `False`
- Corruption log events linked: 7
- Repair scope: Repaired artifacts were not available in this run, so this report only concludes baseline vs corrupted impact.

## Corruption Log Evidence
- `age_published_date`: 1
- `blank_summary`: 1
- `drop_latest_record`: 2
- `duplicate_record`: 1
- `inject_noise`: 1
- `truncate_title`: 1

## Data Quality Signals That Changed
| Signal | Baseline | Corrupted | Delta | Status | Evidence | Interpretation |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| Row count | 22.0000 | 21.0000 | -1.0000 | degraded | drop_latest_record | Lower row count is evidence of record loss. |
| Missing summary rate | 0.0000 | 0.0476 | +0.0476 | degraded | blank_summary | Higher missing summary rate reduces evidence available to the embedding and answer. |
| Duplicate paper_id count | 0.0000 | 1.0000 | +1.0000 | degraded | duplicate_record | Duplicate ids can crowd the retrieved context with repeated records. |
| Duplicate row rate | 0.0000 | 0.0476 | +0.0476 | degraded | duplicate_record | Repeated rows make duplicate context measurable. |
| Max age_days | 175.0000 | 402.0000 | +227.0000 | degraded | age_published_date | Aged records are freshness risk evidence. |
| Freshness stale rows | 0.0000 | 1.0000 | +1.0000 | degraded | age_published_date | Stale rows show freshness threshold impact. |

## RAG Metrics With Evidence-Based Changes
| Metric | Baseline | Corrupted | Delta | Status | Impact area |
| :--- | ---: | ---: | ---: | :--- | :--- |
| Mean token F1 | 1.0000 | 0.7000 | -0.3000 | degraded | generation |
| Judge accuracy | 100.00% | 80.00% | -20.00% | degraded | generation |
| Mean judge score | 5.0000 | 4.2333 | -0.7667 | degraded | generation |

## Signals That Did Not Change
These signals are recorded explicitly to avoid over-claiming.

### Data Quality
| Signal | Baseline | Corrupted | Delta | Status | Evidence | Interpretation |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| Missing text_for_embedding rate | 0.0000 | 0.0000 | 0.0000 | unchanged | blank_summary | Embedding text availability did not necessarily change when summary changed. |

### RAG Metrics
| Metric | Baseline | Corrupted | Delta | Status | Impact area |
| :--- | ---: | ---: | ---: | :--- | :--- |
| Retrieval hit rate | 100.00% | 100.00% | 0.00% | unchanged | retrieval |

## Conclusion
The corrupted dataset has quality/freshness evidence linked to the corruption log, and only the RAG metrics with measured deltas are marked as changed. Retrieval hit rate is listed as unchanged when its delta is zero, so the report does not claim retrieval degradation without evidence. The observed degradation is concentrated in answer quality metrics when those metrics have a negative delta.
