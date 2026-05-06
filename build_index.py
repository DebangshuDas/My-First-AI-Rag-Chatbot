from pdf_loader import load_pdf
from chunker import chunk_text
from vector_store import build_index

text = load_pdf("company_policy.pdf")
chunks = chunk_text(text)

build_index(chunks)