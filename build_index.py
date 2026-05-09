from pdf_loader import load_pdf
from chunker import chunk_text
from vector_store import build_index
import os

file_path = "company_policy.pdf"

pages = load_pdf(file_path)

all_chunks = []

for page_data in pages:

    page_number = page_data["page"]
    text = page_data["text"]

    chunks = chunk_text(text)

    for chunk in chunks:

        all_chunks.append({
            "source": os.path.basename(file_path),
            "page": page_number,
            "text": chunk
        })

build_index(all_chunks)