import streamlit as st
from ai_chatbot import agent_response
from prompts import JSON_PROMPT as system_prompt
from chatbot import get_weather
from pdf_loader import load_pdf
from chunker import chunk_text
from vector_store import build_index
import os


# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="AI Assistant", layout="wide")

# ---------------- HEADER ---------------- #
st.title("🤖 AI Assistant")
st.markdown("##### 🚀 Powered by Ollama + Agent + RAG")

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚙️ Settings")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = [
            {"role": "system", "content": system_prompt}
        ]
        st.success("Chat cleared!")

    st.markdown("---")
    st.subheader("📄 Upload PDF")

    uploaded_files = st.file_uploader(
        "Upload company documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Build Knowledge Base"):

        with st.spinner("Building multi-document knowledge base..."):

            UPLOAD_FOLDER = "uploaded_docs"

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            saved_files = []

            for uploaded_file in uploaded_files:

                file_path = os.path.join(
                    UPLOAD_FOLDER,
                    uploaded_file.name
                )

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                saved_files.append(file_path)

            st.success(f"Uploaded {len(saved_files)} PDFs")
            all_text = ""

            chunks = []

            for file_path in saved_files:

                pdf_text = load_pdf(file_path)

                for chunk in chunk_text(pdf_text):

                    chunks.append({
                        "source": os.path.basename(file_path),
                        "text": chunk
                    })

            #     all_text += pdf_text + "\n"

            # chunks = chunk_text(all_text)

            build_index(chunks=chunks)

        st.success("📚 Multi-document knowledge base ready!")

    # ---------------- LIVE WEATHER ---------------- #
    st.markdown("---")
    st.subheader("🌤 Live Weather")

    weather_city = st.text_input(
        "Enter city",
        value="Kolkata"
    )

    if st.button("Get Weather"):

        weather_data = get_weather(weather_city)

        if weather_data:

            col1, col2 = st.columns(2)

            with col1:
                st.metric("🌡 Temp", f"{weather_data['temp']:.2f} °C") # type: ignore
                st.metric("💧 Humidity", f"{weather_data['humidity']} %") # type: ignore

            with col2:
                st.metric("🥵 Feels Like", f"{weather_data['feels_like']:.2f} °C") # type: ignore
                st.metric("📈 Pressure", f"{weather_data['pressure']} hPa") # type: ignore

        else:
            st.error("Could not fetch weather data")

    st.markdown("---")
    st.markdown("### ℹ️ Info")
    st.write("Model: llama3")
    st.write("Features:")
    st.write("- Agent (tool calling)")
    st.write("- Weather API")
    st.write("- Joke API")
    st.write("- RAG (knowledge base)")
    st.markdown("""
        <style>
        .stChatMessage {
            padding: 10px;
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

# ---------------- INIT SESSION ---------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": system_prompt}
    ]

# ---------------- DISPLAY CHAT ---------------- #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- DISPLAY KNOWLEDGE BASE STATUS ---------------- #
if os.path.exists("faiss_index.bin"):
    st.success("📚 Knowledge Base Ready")
else:
    st.warning("⚠️ Upload and build a PDF knowledge base first")

# ---------------- USER INPUT ---------------- #
user_input = st.chat_input("💬 Ask me anything...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # ---------------- AI RESPONSE ---------------- #
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            bot_reply = agent_response(user_input, st.session_state.chat_history)
            st.write(bot_reply)

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # ---------------- LIMIT MEMORY ---------------- #
    st.session_state.chat_history = st.session_state.chat_history[-10:]