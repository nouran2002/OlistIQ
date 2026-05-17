import sys
import os
from dotenv import load_dotenv
from google import genai
import tools_logic as logic
import tools_schemas as schemas
import streamlit as st

load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = (
    "You are Tommy, a proactive Business Intelligence Agent. "
    "CRITICAL: Every time you start a new conversation, your first priority is to "
    "silently run the get_business_health_check tool..."
)

# إنشاء جلسة الشات (مهم تكون بره الدالة عشان تفتكر الكلام)
chat = client.chats.create(
    model="gemini-2.5-flash", # تأكدي من اسم الموديل عندك
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

def run_tommy_agent(user_query):
    try:
        response = chat.send_message(user_query)
        return response.text
    except Exception as e:
        return f"Error: {e}"
