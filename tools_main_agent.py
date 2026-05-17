import streamlit as st
import sys
from google import genai
import tools_logic as logic

sys.stdout.reconfigure(encoding='utf-8')

def get_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

SYSTEM_PROMPT = (
    "You are Tommy, a proactive Business Intelligence Agent. "
    "CRITICAL: Every time you start a new conversation, your first priority is to "
    "silently run the get_business_health_check tool..."
)

# إنشاء جلسة الشات (مهم تكون بره الدالة عشان تفتكر الكلام)
def create_chat():
    client = get_client()
    if not client:
        return None

    return client.chats.create(
        model="gemini-2.5-flash",
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[
                logic.get_revenue_by_range,
                logic.Top_selling_products,
                logic.Detect_sales_anomalies,
                logic.generate_business_insights,
                logic.compare_periods,
                logic.analyze_sales_performance,
                logic.analyze_marketing_efficiency,
                logic.analyze_customer_loyalty,
                logic.get_business_health_check
            ]
        )
    )

def get_chat():
    if "chat" not in st.session_state:
        st.session_state.chat = create_chat()
    return st.session_state.chat

def run_tommy_agent(user_query):
    try:
        chat = get_chat()
        response = chat.send_message(user_query)
        return response.text
    except Exception as e:
        return f"Error: {e}"
