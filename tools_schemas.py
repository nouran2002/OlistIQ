##=====================================================
## JSON schema for each tool
##=====================================================
my_tools_schemas = [
    {
        "name": "get_revenue_by_range",
        "description": "Calculates revenue. IMPORTANT: If the user doesn't provide dates, ask them for a start and end date (format: YYYY-MM-DD).",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string", 
                    "description": "The starting date (format: YYYY-MM-DD), e.g., '2018-01-01'"
                },
                "end_date": {
                    "type": "string", 
                    "description": "The ending date (format: YYYY-MM-DD), e.g., '2018-03-31'"
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "Top_selling_products",
        "description": "Identifies the best-selling product category and its revenue for a given time period. Use this tool when the user asks for the top product or most sold category.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_of_period": {
                    "type": "string", 
                    "description": "The start date of the period (format: YYYY-MM-DD)"
                },
                "end_of_period": {
                    "type": "string",
                    "description": "The end date of the period (format: YYYY-MM-DD)"
                }
            },
            "required": ["start_of_period", "end_of_period"]
        }
    },
    {
        "name": "Detect_sales_anomalies",
        "description": "Checks if a specific date had unusually high sales compared to the average. Use this when the user asks 'Was there a spike on this date?'",
        "parameters": {
            "type": "object",
            "properties": {
                "target_date": {
                    "type": "string",
                    "description": "The date to check (format: YYYY-MM-DD)"
                }
            },
            "required": ["target_date"]
        }
    },
    {
        "name": "generate_business_insights",
        "description": "Provides a high-level summary of customer segments (Champions, Loyal, At-Risk, etc.). Use this tool to answer questions about customer behavior, loyalty, or who the most valuable customers are. Takes no parameters.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "compare_periods",
        "description": "Compares business performance (Revenue, Orders, Customers) between two specific time periods. Use this to answer 'How are we doing compared to last month?'",
        "parameters": {
            "type": "object",
            "properties": {
                "current_start":  {"type": "string", "description": "Start of current period (YYYY-MM-DD)"},
                "current_end":    {"type": "string", "description": "End of current period (YYYY-MM-DD)"},
                "previous_start": {"type": "string", "description": "Start of previous period (YYYY-MM-DD)"},
                "previous_end":   {"type": "string", "description": "End of previous period (YYYY-MM-DD)"}
            },
            "required": ["current_start", "current_end", "previous_start", "previous_end"]
        }
    },
    {
    "name": "analyze_sales_performance",
    "description": "Analyzes monthly revenue trends and finds root cause of biggest drop.",
    "parameters": {
        "type": "object",
        "properties": {}  
    }
    },
    {
    "name": "analyze_marketing_efficiency",
    "description": "Analyzes marketing performance by calculating ROAS (Return on Ad Spend). It identifies the most and least efficient months in terms of budget spending versus revenue generated. Use this for questions about marketing ROI, spend effectiveness, or identifying months where budget was wasted.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
    },
    {
    "name": "analyze_customer_loyalty",
    "description": "Analyzes customer behavior, including retention rate, average Customer Lifetime Value (LTV), and how many customers return for a second purchase. Use this to answer questions about customer loyalty, repeat buyers, or long-term value.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
    }, 
    {
    "name": "get_business_health_check",
    "description": "Automatically scans all business metrics (Sales, Marketing, Customers) to detect anomalies, drop in revenue, or inefficient spending. It provides a list of alerts and actionable recommendations for the business owner.",
    "parameters": { "type": "object", "properties": {}, "required": [] }
    },
    {
    "name": "get_quick_alerts",
    "description": "A lightweight version of the health check to be used as a 'startup notification'.",
    "parameters": { "type": "object", "properties": {}, "required": [] }
}   
]
