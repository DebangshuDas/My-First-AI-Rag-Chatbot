from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
from vector_store import load_index, search

index, chunks = load_index()

# # Step 3: Convert Text → Embeddings
# model = SentenceTransformer('all-MiniLM-L6-v2')

# with open("data.txt", "r") as file:
#     text = file.read()

# # simple chunking
# chunks = text.split("\n")

# embeddings = model.encode(chunks)

# # Step 4: Store in Vector DB (FAISS)

# dimension = embeddings.shape[1]

# index = faiss.IndexFlatL2(dimension)

# embeddings = np.array(embeddings).astype('float32')

# index.add(embeddings) # type: ignore

# # Step 5: Retrieve Relevant Data

# def search(query):
#     query_embedding = np.array(model.encode([query])).astype('float32')
    
#     distances, indices = index.search(query_embedding, k=2) # type: ignore
    
#     results = [chunks[i] for i in indices[0]]
#     return results

# # Step 6: Send Context to Ollama

# def rag_response(query):
#     context = search(query)
#     context_text = "\n".join(context)
    
#     prompt = f"""
#     Answer based only on the context below:

#     Context:
#     {context_text}

#     Question:
#     {query}
#     """

#     response = ollama.chat(
#         model='llama3',
#         messages=[
#             {
#                 "role": "system",
#                 "content": "Answer ONLY from provided context. If not found, say you don't know."
#             },
#             {"role": "user", "content": prompt}
#         ]
#     )

#     return response['message']['content']

# # print(rag_response("When can I sign out from work ?"))

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

    # response = ollama.chat(
    #     model='llama3',
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "Answer ONLY from provided context. If not found, say you don't know."
    #         },
    #         {"role": "user", "content": prompt}
    #     ]
    # )

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