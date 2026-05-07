import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "chunks.pkl"


def build_index(chunks):
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings) # type: ignore

    # Save index
    faiss.write_index(index, INDEX_FILE)

    # Save chunks
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Index built and saved")


def load_index():

    # 🚨 check existence
    if not os.path.exists(INDEX_FILE):
        return None, None

    if not os.path.exists(CHUNKS_FILE):
        return None, None

    index = faiss.read_index(INDEX_FILE)

    with open(CHUNKS_FILE, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


def search(query, index, chunks, k=5):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k)

    return [chunks[i] for i in indices[0]]