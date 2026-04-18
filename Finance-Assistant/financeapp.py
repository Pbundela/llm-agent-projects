import streamlit as st
import ollama
import yfinance as yf

# =========================
# TOOL 1: STOCK PRICE (REAL)
# =========================
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        price = round(data["Close"].iloc[-1], 2)

        return {
            "symbol": symbol,
            "price": price
        }
    except:
        return {"error": "Invalid stock symbol"}


# =========================
# TOOL 2: EMI CALCULATOR
# =========================
def calculate_emi(amount, rate, tenure):
    monthly_rate = rate / (12 * 100)
    emi = (amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)

    return round(emi, 2)


# =========================
# TOOL 3: BUDGET ANALYSIS
# =========================
def analyze_budget(income, expenses):
    savings = income - expenses

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "status": "Good 👍" if savings > 0 else "Overspending ⚠️"
    }


# =========================
# TOOL 4: INVESTMENT ADVICE
# =========================
def suggest_investment(risk_level, amount):
    if risk_level == "low":
        return {
            "plan": "FD / Bonds",
            "expected_return": "5-7%"
        }
    elif risk_level == "medium":
        return {
            "plan": "Mutual Funds",
            "expected_return": "8-12%"
        }
    else:
        return {
            "plan": "Stocks / Crypto",
            "expected_return": "12-20%"
        }


# =========================
# FUNCTION MAP
# =========================
available_functions = {
    "get_stock_price": get_stock_price,
    "calculate_emi": calculate_emi,
    "analyze_budget": analyze_budget,
    "suggest_investment": suggest_investment
}


# =========================
# TOOL SCHEMA
# =========================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get latest stock price",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_emi",
            "description": "Calculate loan EMI",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "rate": {"type": "number"},
                    "tenure": {"type": "integer"}
                },
                "required": ["amount", "rate", "tenure"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_budget",
            "description": "Analyze income vs expenses",
            "parameters": {
                "type": "object",
                "properties": {
                    "income": {"type": "number"},
                    "expenses": {"type": "number"}
                },
                "required": ["income", "expenses"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_investment",
            "description": "Suggest investment based on risk",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_level": {"type": "string"},
                    "amount": {"type": "number"}
                },
                "required": ["risk_level", "amount"]
            }
        }
    }
]


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="AI Finance Assistant", page_icon="💼")

st.title("💼 AI Finance Assistant")
st.write("Ask anything about finance, investments, loans, or budgeting")

user_input = st.text_input("Enter your query:")

if st.button("Analyze") and user_input:

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

    st.success("✅ Analysis Complete")
    st.write(response["message"]["content"])
    
st.title("Test App")
st.write("If you see this, Streamlit works")