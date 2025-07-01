import openai
import os
import faiss
import numpy as np
import pickle
import logging

INDEX_PATH = "static/outputs/faiss.index"
META_PATH = "static/outputs/faiss_meta.pkl"

def get_latest_file_by_topic(topic, outputs_dir="static/outputs"):
    """
    Find the latest .txt file in outputs_dir whose filename contains the topic.
    """
    files = [
        f for f in os.listdir(outputs_dir)
        if topic.lower() in f.lower() and f.endswith(".txt")
    ]
    if not files:
        return None
    # Sort by modified time, descending
    files.sort(key=lambda f: os.path.getmtime(os.path.join(outputs_dir, f)), reverse=True)
    return os.path.join(outputs_dir, files[0])

def store_embedding(topic):
    """
    Loads the latest file for the given topic, generates an embedding, and returns it.
    """
    file_path = get_latest_file_by_topic(topic)
    if not file_path:
        return {"error": f"No file found for topic '{topic}'."}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Generate embedding using OpenAI (or your preferred embedding model)
    response = openai.embeddings.create(
        input=content,
        model="text-embedding-3-small"  # or your preferred model
    )
    embedding = np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)

    # Log the embedding creation
    logging.warning(f"Embedding created for topic: {topic}, file: {file_path}, embedding_dim: {len(embedding)}")

    # Load or create FAISS index
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "rb") as meta_f:
            meta = pickle.load(meta_f)
    else:
        index = faiss.IndexFlatL2(embedding.shape[1])
        meta = []

    # Add embedding and metadata
    index.add(embedding)
    meta.append({"topic": topic, "file": file_path})

    # Save index and metadata
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as meta_f:
        pickle.dump(meta, meta_f)

    return {
        "file": file_path,
        "embedding_dim": embedding.shape[1],
        "index_size": index.ntotal
    }

def search_embeddings(query, top_k=3):
    """
    Given a query string, embed it and retrieve the top_k most similar documents from FAISS.
    Returns a list of dicts with file and similarity score.
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        return {"error": "No embeddings index found."}

    # Embed the query
    response = openai.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_embedding = np.array(response.data[0].embedding, dtype="float32").reshape(1, -1)

    # Load FAISS index and metadata
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as meta_f:
        meta = pickle.load(meta_f)

    # Search for top_k similar embeddings
    D, I = index.search(query_embedding, top_k)
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < len(meta):
            results.append({
                "file": meta[idx]["file"],
                "topic": meta[idx]["topic"],
                "score": float(score)
            })
    return results