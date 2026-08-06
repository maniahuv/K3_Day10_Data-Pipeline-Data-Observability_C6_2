# CP2 - Vai trò 4: RAG index & smoke test

## Kết quả

- Status: PASS
- Clean rows: 22
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Chroma collection: `papers-baseline`
- Persist path: `D:\AI thuc chien\lab10\K3_Day10_Data-Pipeline-Data-Observability_C6_2\data\chroma`
- Embedding manifest: `D:\AI thuc chien\lab10\K3_Day10_Data-Pipeline-Data-Observability_C6_2\data\embeddings\papers_embeddings.json`
- Smoke artifact: `D:\AI thuc chien\lab10\K3_Day10_Data-Pipeline-Data-Observability_C6_2\data\results\role4_cp2_smoke.json`

## Semantic search

- Query: `retrieval augmented generation large language model`
- Top 1: `10.55041/isjem07213` | score=0.6643 | Speculative Retrieval-Augmented Generation for Cost-Efficient Large Language Model Inference
- Top 2: `10.20944/preprints202604.0339.v1` | score=0.6265 | Retrieval-Augmented Large Language Model Agents for Automated Scientific Literature Review Generation
- Top 3: `10.35314/3y9hy151` | score=0.6147 | Implementation of Retrieval-Augmented Generation Method on Large Language Model for Development of Campus Service and Information Chatbot

## Exact lookup

- Lookup by paper_id: PASS
- Lookup by exact title: PASS
- Tested paper_id: `10.2118/234689-pa`

## QA smoke test

- Question: `What is the paper 'SafeRAG: A Large-Language-Model-Based Multistage Retrieval-Augmented Framework for Oil and Gas Safety Report Generation' about?`
- Retrieved first doc: `10.2118/234689-pa`
- Answer preview: Summary In high-risk industrial settings, leveraging large language models (LLMs) for automated accident analysis and generating safety reports has emerged as an efficient workflow.

## Ghi chú

CP2 đã build baseline collection thật. Agent LLM thật có thể test sau khi provider key trong `.env` sẵn sàng; smoke test hiện dùng retrieval + QA rule-based nên không cần API key.
