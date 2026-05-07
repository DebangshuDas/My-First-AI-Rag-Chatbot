from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
from vector_store import load_index, search

index, chunks = load_index()


def rag_response(query):

    context = search(query, index, chunks)
    context_text = "\n".join(context)

    prompt = f"""
        You are a company HR assistant.

        Answer the user's question ONLY using the provided context.

        If the answer exists in context:
        - provide complete details
        - summarize clearly
        - do not mention sections only

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