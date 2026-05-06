from dotenv import load_dotenv

from transformer import rag_response

load_dotenv()

from datetime import datetime
import requests
import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
def run_chatbot():
    print("Hello, welcome in our chatbot. type \"exit\" to close.")
    system_prompt = choose_mode()

    global chat_history
    chat_history = [
        {"role": "system", "content": system_prompt}
    ]

    while True:
        user_input = input("You: ").lower()

        if user_input == "exit":
            print("Bot: Thanks for your valuable time. Exiting...")
            break

        elif "load" in user_input: 
            print("-------------------Chat history:------------------ \n")
            load_file_content()
            print("-------------------end of file--------------------")

        elif "clean" in user_input or "clear" in user_input:
            clear_history()

        else:
            
            response = get_response(user_input=user_input)
            print("Bot: ", response)
            save_in_file(user_input, response)


def save_in_file(user_input, response):

    with open("chat_history.txt", "a") as file:
        file.write(f"User: {user_input} \n")
        file.write(f"Bot: {response} \n")
        
def load_file_content():
    try:
        with open("chat_history.txt", "r") as file:
            print(file.read())

    except FileNotFoundError:
        print("Sorry, no previous chat found.")

def clear_history():

    with open("chat_history.txt", "w") as file:
        pass
    print("------------------Chat cleared-------------------")
    global chat_history
    chat_history = [
        {"role" : "system", "content" : choose_mode()}
    ]

def get_response(user_input:str):

    if user_input == "exit":
        return ""
    elif "hi" in user_input or "hello" in user_input :
        return "Hi! how can I help you ?"
    elif "name" in user_input:
        return "I am your Python chatbot."
    elif "date" in user_input:
        return datetime.now().strftime("%A, %d %B %Y")
    elif "joke" in user_input:
        return get_joke()
    elif "weather" in user_input:
        city = extract_city(user_input)     #user_input.strip()[10:]      #fixing the user input "weather in {city}"
        return get_weather(city)
    elif "policy" in user_input or "leave" in user_input:
        return rag_response(user_input)
    else:
    
        chat_history.append({'role': 'user', 'content': user_input})
        bot_reply = get_ai_response()
        chat_history.append({'role': 'assistant', 'content': bot_reply}) # type: ignore
        return bot_reply

def get_joke():
    try:
        url = "https://official-joke-api.appspot.com/random_joke"
        
        response = requests.get(url)
        data = response.json()
        
        return f"{data['setup']} - {data['punchline']}"
    except:

        return "Sorry! I couldn't find any jokes"

import json

def dict_to_json_string(data):
    return json.dumps(data, indent=2)

def json_to_readable_string(data):
    return ", ".join(f"{key}: {value}" for key, value in data.items())

def format_weather(data):
    return (
        f"Temperature: {data['temp']}°C\n"
        f"Feels like: {data['feels_like']}°C\n"
        f"Min: {data['temp_min']}°C\n"
        f"Max: {data['temp_max']}°C\n"
        f"Humidity: {data['humidity']}%\n"
        f"Pressure: {data['pressure']} hPa"
    )

def get_weather(city):
    try:
        api_key = os.getenv("WEATHER_API_KEY")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        response = requests.get(url)
        data = response.json()
        if "main" not in data:
            return "City not found."
        temp = data["main"]["temp"]

        print(f"Weather in {city}: ", data["main"])
        return data["main"] #f"Temperature in {city} is {temp}°C"
    except:
        return "Sorry! I couldn't find weather data."
    
def extract_city(text):
    words = text.split()
    if "in" in words:
        return words[words.index("in") + 1]
    return "Kolkata"

# ---------------- AI FUNCTION ---------------- #

def get_ai_response():
    # response = ollama.chat(
    #     model='llama3',
    #     messages=chat_history
    # )
    # return response['message']['content']

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_history # type: ignore
    )

    reply = response.choices[0].message.content

def choose_mode():
    print("Select Mode:")
    print("1. Normal Assistant")
    print("2. Interviewer")
    print("3. Coding Mentor")

    choice = input("Enter choice: ")

    if choice == "2":
        return """You are a technical interviewer.
        
        Rules:
        - Ask one question at a time
        - Wait for user's answer
        - Evaluate the answer
        - Give feedback
        - Keep responses short
        """
    
    elif choice == "3":
        return """You are a coding mentor.
        Explain concepts simply and guide step-by-step."""
    
    else:
        return "You are a helpful AI assistant."

# run_chatbot()