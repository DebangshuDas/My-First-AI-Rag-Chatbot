import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
import logging

from prompts import JSON_PROMPT
logging.getLogger("transformers").setLevel(logging.ERROR)

from chatbot import get_joke, get_weather
from transformer import rag_response

system_prompt = """
You are an intelligent AI assistant.

You have access to these tools:

1. weather(city) → Get weather info
2. joke() → Get a random joke
3. rag(query) → Answer from company knowledge base

Instructions:

- If user asks about weather → call weather(city)
- If user asks for joke → call joke()
- If user asks about company policy or knowledge → call rag(query)
- Otherwise → answer normally

Tool call format (STRICT):

TOOL_CALL: tool_name(input)

Examples:

User: tell me a joke
Assistant: TOOL_CALL: joke()

User: what is weather in Kolkata
Assistant: TOOL_CALL: weather(Kolkata)

User: what is leave policy
Assistant: TOOL_CALL: rag(leave policy)

Rules:
- Always choose correct tool
- Extract correct input (e.g., city name)
- Do NOT repeat previous tool blindly
- Do NOT guess tool randomly
"""

def tool_weather(city):
    return get_weather(city)

def tool_joke():
    return get_joke()

def tool_rag(query):
    return rag_response(query)

def extract_json(reply):
    import re

    matches = re.findall(r"\{[\s\S]*?\}", reply)

    for m in matches:
        try:
            return json.loads(m)
        except:
            continue

    return None

def extract_city(text):
    words = text.split()
    if "in" in words:
        return words[words.index("in") + 1]
    return "Kolkata"

def agent_response(user_input, chat_history):

    chat_history.append({
        "role": "user", 
        "content": user_input
    })

    # STEP 1: decision (clean context)
    messages = [
        {"role": "system", "content": JSON_PROMPT},
        {"role": "user", "content": user_input}
    ]

    print("Chat_History: ", chat_history, "\nMessages: ", messages)

    # response = ollama.chat(
    #     model='llama3',
    #     messages=messages
    # )

    # reply = response['message']['content']
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    reply = response.choices[0].message.content

    print("RAW JSON:", reply)

    data = extract_json(reply)

    if not data:
        print("⚠️ No valid JSON found")

        user_lower = user_input.lower()

        if any(word in user_lower for word in ["policy", "leave", "company"]):
            print("⚡ Hard override → RAG")

            return handle_tool_json({
                "tool": "rag",
                "input": user_input
            }, chat_history)
        
        if any(word in user_lower for word in ["joke", "funny"]):
            print("⚡ Hard override → joke")

            return handle_tool_json({
                "tool": "joke",
            }, chat_history)
        
        if any(word in user_lower for word in ["weather", "temperature", "season"]):
            print("⚡ Hard override → weather")

            return handle_tool_json({
                "tool": "weather",
                "input": extract_city(user_lower)
            }, chat_history)

        # fallback
        return "Error: Model did not return valid JSON"

    tool = data.get("tool")

    # STEP 2: normal response
    if tool == "none":
        response_text = data.get("response", "")

        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response_text})

        return response_text

    return handle_tool_json(data, chat_history)


def handle_tool_json(data, chat_history):

    tool = data.get("tool")
    argument = data.get("input", "")

    TOOLS = {
        "weather": tool_weather,
        "joke": tool_joke,
        "rag": tool_rag
    }

    tool_func = TOOLS.get(tool)

    if not tool_func:
        return "Unknown tool"

    # Execute tool
    if tool == "weather":

        result = tool_func(argument)

        if not result:
            return "Sorry! I couldn't find weather data."

        user_text = chat_history[-1]["content"].lower()

        if "temperature" in user_text:
            response = f"Current temperature in {argument}: {result['temp']:.2f}°C"

        elif "pressure" in user_text:
            response = f"Current atmospheric pressure in {argument}: {result['pressure']} hPa"

        elif "humidity" in user_text:
            response = f"Current humidity in {argument}: {result['humidity']}%"

        else:
            response = (
                f"Weather in {argument}:\n"
                f"🌡 Temperature: {result['temp']:.2f}°C\n"
                f"🥵 Feels like: {result['feels_like']:.2f}°C\n"
                f"💧 Humidity: {result['humidity']}%\n"
                f"📈 Pressure: {result['pressure']} hPa"
            )

        chat_history.append({
            "role": "assistant",
            "content": response
        })

        return response
    
    if tool == "joke":
        result = tool_joke()
        chat_history.append({
            "role": "assistant",
            "content": result
        })
        return result
    
    if argument:
        result = tool_func(argument)
    else:
        result = tool_func()

    print("Tool result: ", result)

    # 🎯 Direct tools (like joke)

    # 🧠 Use LLM for formatting (weather, rag)
    RESPONSE_PROMPT = """
    You are an assistant.

    Convert the following into a clean natural response:

    # Response according to user_prompt, don't give extra response data

    # like for weather related data, 
    # -if user asks for all weather related data,
    # -then provide all weather data, 
    # -but if asked only temperature or humidity, only answer for that
    # -DO NOT change or round figure numeric data like temperature or atmospheric pressure
    """

    print("Chat_History: ", chat_history)


    # final_response = ollama.chat(
    #     model='llama3',
    #     messages=[
    #         {"role": "system", "content": RESPONSE_PROMPT},
    #         {"role": "user", "content": result}
    #     ]
    # )

    # if 'message' in final_response:
    #     chat_history.append({
    #         "role": "assistant",
    #         "content": final_response['message']['content']
    #     })

    #     return final_response['message']['content']
    
    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": RESPONSE_PROMPT},
            {"role": "user", "content": result}
        ]
    )
    if final_response.choices[0] and final_response.choices[0].message:
        reply = final_response.choices[0].message.content
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply
    
    return "No Natural response found."


def chat():
    print("Welcome to chatbot. type \"exit\" to leave.")
    global chat_history
    chat_history = [{"role": "system", "content": system_prompt}]

    while True:
        raw_input = input("You: ")
        user_input = raw_input.lower()
        if user_input == "exit":
            print("Exiting....")
            break
        print("Bot: ", agent_response(raw_input, chat_history))

# chat()