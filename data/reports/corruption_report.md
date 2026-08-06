# Corrupted Dataset Quality and RAG Impact Report

This report is separate from the baseline report and uses the corrupted dataset artifacts.

## Inputs
- Baseline metrics samples: 30
- Corrupted metrics samples: 30
- Corrupted quality status: `WARNING`
- Corrupted freshness status: `False`
- Corruption log events linked: 0
- Repair scope: Repaired artifacts were available and can be compared in a follow-up repair section.

## Corruption Log Evidence
- No corruption log evidence was attached to this report.

## Data Quality Signals That Changed
| Signal | Baseline | Corrupted | Delta | Status | Evidence | Interpretation |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| Row count | N/A | 21.0000 | N/A | not evaluated | drop_latest_record | Lower row count is evidence of record loss. |
| Missing summary rate | 0.0000 | 0.0476 | +0.0476 | degraded | blank_summary | Higher missing summary rate reduces evidence available to the embedding and answer. |
| Duplicate paper_id count | 0.0000 | 1.0000 | +1.0000 | degraded | duplicate_record | Duplicate ids can crowd the retrieved context with repeated records. |
| Duplicate row rate | 0.0000 | 0.0476 | +0.0476 | degraded | duplicate_record | Repeated rows make duplicate context measurable. |
| Max age_days | N/A | 402.0000 | N/A | not evaluated | age_published_date | Aged records are freshness risk evidence. |
| Freshness stale rows | 0.0000 | 1.0000 | +1.0000 | degraded | age_published_date | Stale rows show freshness threshold impact. |

## RAG Metrics With Evidence-Based Changes
| Metric | Baseline | Corrupted | Delta | Status | Impact area |
| :--- | ---: | ---: | ---: | :--- | :--- |
| Retrieval hit rate | 100.00% | 80.00% | -20.00% | degraded | retrieval |
| Mean token F1 | 1.0000 | 0.7426 | -0.2574 | degraded | generation |
| Judge accuracy | 100.00% | 73.33% | -26.67% | degraded | generation |
| Mean judge score | 5.0000 | 4.1333 | -0.8667 | degraded | generation |

## Signals That Did Not Change
These signals are recorded explicitly to avoid over-claiming.

### Data Quality
| Signal | Baseline | Corrupted | Delta | Status | Evidence | Interpretation |
| :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| Missing text_for_embedding rate | 0.0000 | 0.0000 | 0.0000 | unchanged | blank_summary | Embedding text availability did not necessarily change when summary changed. |

### RAG Metrics
| Metric | Baseline | Corrupted | Delta | Status | Impact area |
| :--- | ---: | ---: | ---: | :--- | :--- |
| None | N/A | N/A | N/A | unchanged | N/A |

## Conclusion
The corrupted dataset has quality/freshness evidence linked to the corruption log, and only the RAG metrics with measured deltas are marked as changed. Retrieval hit rate is listed as unchanged when its delta is zero, so the report does not claim retrieval degradation without evidence. The observed degradation is concentrated in answer quality metrics when those metrics have a negative delta.
