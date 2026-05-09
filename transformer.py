from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
from vector_store import load_index, search



def rag_response(query):
    index, chunks = load_index()

    if index is None or chunks is None:
        return "No knowledge base found. Please upload a PDF first."

    context = search(query, index, chunks)
    # context_text = "\n".join(context)

    context_text = "\n\n".join(
        [
            f"Source: {chunk['source']} | Page: {chunk['page']}\n{chunk['text']}"
            for chunk in context
        ]
    )

    prompt = f"""
        You are an enterprise legal AI assistant.

        Answer ONLY using the provided context.

        Rules:
        - summarize clearly
        - NEVER hallucinate
        - if answer not found, say so
        - ALWAYS mention source document names
        - ALWAYS mention page numbers
        - cite sources clearly

        Context:
        {context_text}

        Question:
        {query}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY from provided context. If not found, say you don't know."
            },
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content

    return reply