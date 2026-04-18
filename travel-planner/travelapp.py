import streamlit as st
import requests
import ollama
import os

# =========================
# CONFIG (ADD YOUR API KEYS)
# =========================
OPENWEATHER_API_KEY = "YOUR OPENWEATHER_API_KEY"
AVIATIONSTACK_API_KEY = "YOUR AVIATIONSTACK_API_KEY"

# =========================
# TOOL FUNCTIONS (REAL APIs)
# =========================

# TOOL 1: Weather API
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if response.get("main"):
        return {
            "city": city,
            "temperature": response["main"]["temp"],
            "weather": response["weather"][0]["description"]
        }
    return {"error": "City not found"}


# TOOL 2: Flight Price (Mock realistic logic)
def get_flight_price(source, destination):
    # Aviationstack is mostly flight data, not pricing
    # So we simulate pricing realistically
    base_price = 4000
    distance_factor = len(source) * len(destination) * 10

    return {
        "source": source,
        "destination": destination,
        "price": base_price + distance_factor
    }


# TOOL 3: Itinerary
def suggest_itinerary(city, days, budget):
    return {
        "city": city,
        "days": days,
        "budget": budget,
        "plan": [
            f"Day 1: Arrival in {city}, relax",
            f"Day 2: Explore top attractions in {city}",
            f"Day 3: Food + shopping + departure"
        ]
    }


available_functions = {
    "get_weather": get_weather,
    "get_flight_price": get_flight_price,
    "suggest_itinerary": suggest_itinerary
}


# =========================
# TOOL SCHEMA
# =========================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_price",
            "description": "Get flight cost between cities",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "destination": {"type": "string"}
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_itinerary",
            "description": "Create travel plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "days": {"type": "integer"},
                    "budget": {"type": "integer"}
                },
                "required": ["city", "days", "budget"]
            }
        }
    }
]


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="AI Travel Planner", page_icon="🌍")

st.title("🌍 AI Travel Planner")
st.write("Plan your trips using AI + real-time tools")

user_input = st.text_input("Enter your travel request:")

if st.button("Plan Trip") and user_input:

    messages = [{"role": "user", "content": user_input}]

    response = ollama.chat(
        model="deepseek-v3.1:671b-cloud ",
        messages=messages,
        tools=tools
    )

    # TOOL LOOP
    while True:
        tool_calls = response["message"].get("tool_calls")

        if not tool_calls:
            break

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]

            function_to_call = available_functions[tool_name]
            result = function_to_call(**tool_args)

            messages.append(response["message"])
            messages.append({
                "role": "tool",
                "content": str(result)
            })

        response = ollama.chat(
            model="deepseek-v3.1:671b-cloud",
            messages=messages
        )

    st.success("Trip Plan Ready!")
    st.write(response["message"]["content"])
