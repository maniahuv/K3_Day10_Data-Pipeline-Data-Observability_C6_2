import json
from pathlib import Path

def audit():
    manifest_path = Path("data/embeddings/papers_embeddings.json")
    if not manifest_path.exists():
        print(f"Error: manifest file {manifest_path} not found.")
        return
        
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("--- Embedding Manifest Audit Report ---")
    print(f"File Path: {manifest_path}")
    print(f"Backend: {data.get('backend')}")
    print(f"Embedding Model: {data.get('embedding_model')}")
    print(f"Collection Name: {data.get('collection_name')}")
    
    docs = data.get('documents', [])
    print(f"Document Count in Manifest: {len(docs)}")
    
    if docs:
        print("\nSample Document:")
        print(f"  - Record ID: {docs[0].get('record_id')}")
        print(f"  - Paper ID: {docs[0].get('paper_id')}")
        print(f"  - Title: {docs[0].get('title')}")
        
if __name__ == "__main__":
    audit()
