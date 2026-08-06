# CP3 - Vai trò 4: Baseline RAG audit

## Kết quả

- Status: PASS
- Clean rows: 22
- Manifest documents: 22
- Collection: `papers-baseline`
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- JSON evidence: `D:\AI thuc chien\lab10\K3_Day10_Data-Pipeline-Data-Observability_C6_2\data\results\role4_cp3_baseline_audit.json`

## Audit manifest/index

- Row count matches: `True`
- Paper IDs match: `True`
- Collection name matches `papers-baseline`: `True`
- Loaded Chroma collection matches: `True`
- Embedding model matches settings: `True`

## Demo semantic search

- Query: `retrieval augmented generation large language model`
- Top 1: `10.55041/isjem07213` | score=0.6643 | Speculative Retrieval-Augmented Generation for Cost-Efficient Large Language Model Inference
- Top 2: `10.20944/preprints202604.0339.v1` | score=0.6265 | Retrieval-Augmented Large Language Model Agents for Automated Scientific Literature Review Generation
- Top 3: `10.35314/3y9hy151` | score=0.6147 | Implementation of Retrieval-Augmented Generation Method on Large Language Model for Development of Campus Service and Information Chatbot

## Demo exact lookup

- Lookup paper_id `10.2118/234689-pa`: `PASS`
- Lookup exact title: `PASS`

## Agent factual answer evidence

- Agent smoke status: `pass`
- Used tool before answer: `True`
- Evidence path: `D:\AI thuc chien\lab10\K3_Day10_Data-Pipeline-Data-Observability_C6_2\data\results\role4_cp2_agent_smoke.json`

## Ghi chú

CP3 role4 chỉ audit baseline RAG artifacts và demo retrieval/agent evidence. Baseline metrics/report toàn pipeline phụ thuộc role evaluation/observability/integrator.
