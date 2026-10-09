import json
import urllib.request
import urllib.parse
from langgraph.graph import StateGraph, END
from state import AgentState
from tools.finance_tools import get_stock_info, get_historical_prices

# ==========================================
# 1. THE NODES (Our Agents)
# ==========================================

def researcher_agent(state: AgentState):
    """Agent 1: Responsible for gathering all data."""
    ticker = state['ticker']
    print(f"🕵️ Researcher: Fetching financial data for {ticker}...")
    
    current_info = get_stock_info(ticker)
    history = get_historical_prices(ticker)
    
    return {
        "financial_data": {
            "current": current_info,
            "history": history
        }
    }

def analyst_agent(state: AgentState):
    """Agent 2: Responsible for writing the final report."""
    print(f"✍️ Analyst: Writing report based on gathered data...")
    
    data = state['financial_data']
    
    prompt = f"""
    You are an elite financial analyst.
    Write a brief, punchy executive summary for {state['ticker']} based on this raw data:
    {json.dumps(data, indent=2)}
    
    Include:
    1. The company name and current price.
    2. A brief analysis of the recent historical price trend.
    
    CRITICAL RULES:
    - Use clean Markdown formatting (bolding, bullet points).
    - DO NOT include any advertisements, promotional links, or watermarks.
    - Output ONLY the professional financial summary, nothing else.
    """
    
    try:
        prompt_encoded = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{prompt_encoded}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            report_text = response.read().decode('utf-8')
            
    except Exception as e:
        report_text = f"The free AI endpoint failed. Error: {str(e)}"
    
    # We removed the ugly '=== AI REPORT ===' formatting!
    return {"final_report": report_text}


# ==========================================
# 2. THE GRAPH (The Controller / Router)
# ==========================================

def build_team():
    workflow = StateGraph(AgentState)
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("analyst", analyst_agent)
    
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", END)
    
    return workflow.compile()


# ==========================================
# 3. RUN IT
# ==========================================
if __name__ == "__main__":
    app = build_team()
    
    initial_request = {
        "ticker": "AAPL",
        "messages": [],
        "financial_data": {},
        "final_report": ""
    }
    
    final_state = app.invoke(initial_request)
    print("\n" + final_state['final_report'])
