import streamlit as st
import ollama
import inspect

# =========================
# INVENTORY WITH BRANDS
# =========================
inventory_db = {
    "laptop": {
        "default": {"stock": 5, "price": 50000},
        "dell": {"stock": 3, "price": 55000},
        "hp": {"stock": 2, "price": 52000}
    },
    "phone": {"stock": 10, "price": 20000},
    "headphones": {"stock": 25, "price": 2000},
    "monitor": {"stock": 0, "price": 15000}
}

# =========================
# NLP: PRODUCT + BRAND
# =========================
def extract_product_and_brand(text):
    text = text.lower()

    products = ["laptop", "phone", "headphones", "monitor"]
    brands = ["dell", "hp", "apple", "lenovo"]

    product = None
    brand = None

    for p in products:
        if p in text:
            product = p

    for b in brands:
        if b in text:
            brand = b

    return product, brand


# =========================
# TOOL 1: INVENTORY
# =========================
def check_inventory(product_name, brand=None):
    product = product_name.lower()

    if product in inventory_db:
        data = inventory_db[product]

        if isinstance(data, dict) and brand:
            if brand in data:
                return data[brand]

        return data.get("default", data)

    return {"stock": 0, "price": None}


# =========================
# TOOL 2: RECOMMEND
# =========================
def recommend_products(budget, category):
    products = [
        {"name": "laptop", "price": 50000},
        {"name": "phone", "price": 20000},
        {"name": "headphones", "price": 2000}
    ]
    return [p for p in products if p["price"] <= budget]


# =========================
# TOOL 3: COUPON
# =========================
def apply_coupon(price=None, coupon_code=None):
    if price is None:
        return {"error": "Missing price"}

    coupons = {"SAVE10": 0.10, "SAVE20": 0.20}

    discount = coupons.get(coupon_code.upper(), 0)
    final_price = price * (1 - discount)

    return {
        "final_price": round(final_price, 2),
        "discount": f"{int(discount*100)}%"
    }


# =========================
# TOOL 4: DELIVERY
# =========================
def estimate_delivery(pincode):
    return {
        "pincode": pincode,
        "delivery_days": 3 if int(pincode) % 2 == 0 else 5
    }


# =========================
# TOOL 5: SUMMARY
# =========================
def create_order_summary(product, price, stock):
    return {
        "product": product,
        "price": price,
        "availability": "In Stock" if stock > 0 else "Out of Stock"
    }


# =========================
# FUNCTION MAP
# =========================
available_functions = {
    "check_inventory": check_inventory,
    "recommend_products": recommend_products,
    "apply_coupon": apply_coupon,
    "estimate_delivery": estimate_delivery,
    "create_order_summary": create_order_summary
}

# =========================
# TOOL SCHEMA
# =========================
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Get product price and stock first",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "brand": {"type": "string"}
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_coupon",
            "description": "Apply discount after getting price",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number"},
                    "coupon_code": {"type": "string"}
                },
                "required": ["coupon_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_delivery",
            "description": "Estimate delivery time",
            "parameters": {
                "type": "object",
                "properties": {
                    "pincode": {"type": "string"}
                },
                "required": ["pincode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_order_summary",
            "description": "Generate final summary",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                    "price": {"type": "number"},
                    "stock": {"type": "number"}
                },
                "required": ["product", "price", "stock"]
            }
        }
    }
]

# =========================
# UI
# =========================
st.set_page_config(page_title="AI E-commerce Assistant", page_icon="🛒")

st.title("🛒 AI E-commerce Assistant")
st.write("Smart shopping powered by AI")

user_input = st.text_input("Ask something:")

if st.button("Run") and user_input:

    product, brand = extract_product_and_brand(user_input)

    messages = [
        {
            "role": "system",
            "content": """You are an e-commerce assistant.

Steps:
1. Check inventory
2. Apply coupon
3. Estimate delivery
4. create_order_summary

Always follow order."""
        },
        {"role": "user", "content": user_input}
    ]

    response = ollama.chat(
        model="deepseek-v3.1:671b-cloud ",
        messages=messages,
        tools=tools
    )

    while True:
        tool_calls = response["message"].get("tool_calls")

        if not tool_calls:
            break

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]

            func = available_functions[tool_name]

            # FILTER ARGS
            valid_params = inspect.signature(func).parameters
            filtered_args = {k: v for k, v in tool_args.items() if k in valid_params}

            # AUTO FIX
            if tool_name == "check_inventory":
                if product:
                    filtered_args["product_name"] = product
                    if brand:
                        filtered_args["brand"] = brand

            if tool_name == "apply_coupon":
                if "price" not in filtered_args and product:
                    inv = check_inventory(product, brand)
                    filtered_args["price"] = inv["price"]

            if tool_name == "create_order_summary":
                if product:
                    inv = check_inventory(product, brand)
                    filtered_args["product"] = f"{brand} {product}" if brand else product
                    filtered_args["price"] = inv["price"]
                    filtered_args["stock"] = inv["stock"]

            result = func(**filtered_args)

            messages.append(response["message"])
            messages.append({
                "role": "tool",
                "content": str(result)
            })

        response = ollama.chat(
            model="deepseek-v3.1:671b-cloud ",
            messages=messages
        )

    st.success("✅ Done")
    st.write(response["message"]["content"])