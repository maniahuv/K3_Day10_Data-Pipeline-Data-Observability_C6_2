# Baseline vs Corrupted vs Repaired Comparison

This report is generated from persisted metrics, data quality, freshness, and corruption log artifacts.

## Artifact Scope
- Baseline metrics samples: 30
- Corrupted metrics samples: 30
- Repaired metrics samples: 30
- Corruption events linked: 7
- Baseline quality status: `PASSED`
- Corrupted quality status: `WARNING`
- Repaired quality status: `PASSED`

## Corruption Evidence
- `age_published_date`: 1
- `blank_summary`: 1
- `drop_latest_record`: 2
- `duplicate_record`: 1
- `inject_noise`: 1
- `truncate_title`: 1

## Evaluation Metrics
| Metric | Baseline | Corrupted | Repaired | Corrupted - Baseline | Repaired - Baseline |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Retrieval hit rate | 100.00% | 80.00% | 100.00% | -20.00% | 0.00% |
| Mean token F1 | 1.0000 | 0.7426 | 1.0000 | -0.2574 | 0.0000 |
| Judge accuracy | 100.00% | 73.33% | 100.00% | -26.67% | 0.00% |
| Mean judge score | 5.0000 | 4.1333 | 5.0000 | -0.8667 | 0.0000 |

## Data Quality Signals
| Signal | Baseline | Corrupted | Repaired | Corrupted - Baseline | Repaired - Baseline |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Row count | 22.0000 | 21.0000 | 22.0000 | -1.0000 | 0.0000 |
| Summary missing rate | 0.00% | 4.76% | 0.00% | +4.76% | 0.00% |
| Embedding text missing rate | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| Duplicate paper_id count | 0.0000 | 1.0000 | 0.0000 | +1.0000 | 0.0000 |
| Duplicate row rate | 0.00% | 4.76% | 0.00% | +4.76% | 0.00% |
| Max age_days | 175.0000 | 402.0000 | 175.0000 | +227.0000 | 0.0000 |
| Quality status | PASSED | WARNING | PASSED | N/A | N/A |

## Freshness Signals
| Signal | Baseline | Corrupted | Repaired | Corrupted - Baseline | Repaired - Baseline |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Stale rows | 0.0000 | 1.0000 | 0.0000 | +1.0000 | 0.0000 |
| Is fresh | True | False | True | N/A | N/A |

## Recovery Assessment
Recovery is complete for the measured signals and metrics in this run.

- No repaired quality, freshness, or evaluation metric remains worse than baseline.

## Conclusion Limits
- This is an artifact-level comparison over the current fixed test set and current persisted datasets; it is not a statistical proof across future data.
- RAGAS was skipped in the metrics artifacts, so the conclusion is limited to retrieval hit rate, token F1, judge accuracy, and judge score.
- The corruption log explains the intended data faults, but it does not isolate one fault at a time. Metric movement should be attributed to the corrupted dataset as a bundle, not to a single event without an ablation.
- If future repaired artifacts leave any quality, freshness, or evaluation signal worse than baseline, recovery must be reported as incomplete.
