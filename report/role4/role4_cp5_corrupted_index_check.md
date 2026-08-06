# CP5 - Vai trò 4: Corrupted index check

## Kết quả

- Status: PASS
- Corrupted source: `D:\AI thuc chien\lab10\K3_Day10_Data-Pipeline-Data-Observability_C6_2\data\clean\papers_clean_corrupted.csv`
- Corrupted rows: 21
- Baseline collection: `papers-baseline`
- Corrupted collection: `papers-corrupted`
- Baseline rebuilt before check: `False`
- Baseline rebuilt after corrupted build: `False`
- Baseline still readable: `True`
- Baseline not mutated: `True`

## Baseline query

`retrieval augmented generation large language model`

## Baseline top IDs before

- `10.55041/isjem07213`
- `10.20944/preprints202604.0339.v1`
- `10.35314/3y9hy151`

## Corrupted top IDs

- `10.55041/isjem07213`
- `10.20944/preprints202604.0339.v1`
- `10.35314/3y9hy151`

## Baseline top IDs after

- `10.55041/isjem07213`
- `10.20944/preprints202604.0339.v1`
- `10.35314/3y9hy151`

## Dropped-record lookup check

- `10.2118/234689-pa` baseline_found=`True`, corrupted_found=`False`
- `10.1007/s10278-026-02086-9` baseline_found=`True`, corrupted_found=`False`
