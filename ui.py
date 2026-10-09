import streamlit as st
import pandas as pd
from agent import build_team
from tools.finance_tools import get_historical_prices

# 1. Web Page Setup
st.set_page_config(page_title="Financial Agent UI", page_icon="📈", layout="wide")

# --- SIDEBAR NUDGE ---
with st.sidebar:
    st.header("💡 Need Inspiration?")
    st.write("Here are some of the most popular stocks to research:")
    st.markdown("""
    * **AAPL** - Apple Inc.
    * **MSFT** - Microsoft
    * **NVDA** - NVIDIA
    * **TSLA** - Tesla
    * **AMZN** - Amazon
    * **META** - Meta Platforms
    * **GOOG** - Alphabet (Google)
    * **BRK-B** - Berkshire Hathaway
    * **JPM** - JPMorgan Chase
    * **V** - Visa
    * **WMT** - Walmart
    * **JNJ** - Johnson & Johnson
    * **NFLX** - Netflix
    """)
    st.info("Type any of these tickers into the chat box to get started!")

st.title("📈 Multi-Agent Financial Analyst")

# --- INTRO SECTION ---
with st.expander("👋 About This Project & Architecture (Play Audio)", expanded=True):
    st.write("**Hi, I'm Rayyan!** Listen to a quick breakdown of how I built this production-ready AI architecture:")
    
    try:
        st.audio("intro.mp3")
    except Exception:
        st.caption("(Audio file not found yet. Make sure intro.mp3 is in the folder!)")
        
    st.markdown("""
    **Project Highlights:**
    * **Multi-Agent Architecture:** Built using LangGraph to route tasks safely between specialized agents.
    * **State Management:** Uses strictly-typed state schemas to manage agent memory deterministically.
    * **Tool Execution:** A *Researcher Agent* securely fetches market data via Python APIs (yfinance).
    * **LLM Synthesis:** An *Analyst Agent* reads the state and synthesizes the raw numbers into an executive summary.
    """)

st.write("---")
st.write("Enter a stock ticker below. The **Researcher Agent** will fetch real-time data, and the **Analyst Agent** will write a report.")

# 2. Memory for the UI (so chat doesn't disappear when you type again)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Draw all previous messages on the screen
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. Chat Input Box
if user_input := st.chat_input("Enter a ticker (e.g., AAPL, TSLA, NVDA)..."):
    
    # Instantly show the user's message on screen
    with st.chat_message("user"):
        st.markdown(user_input.upper())
    st.session_state.chat_history.append({"role": "user", "content": user_input.upper()})
    
    # Start the Agent!
    with st.chat_message("assistant"):
        with st.spinner(f"Agents are researching {user_input.upper()}..."):
            
            # Build our LangGraph team
            app = build_team()
            
            # Feed the user's ticker into our State memory
            initial_state = {
                "ticker": user_input.upper(),
                "messages": [],
                "financial_data": {},
                "final_report": ""
            }
            
            # Run the system
            final_state = app.invoke(initial_state)
            
            # Extract the final report
            report = final_state['final_report']
            safe_report = report.replace("$", r"\$")
            
            # Show the report
            st.markdown(safe_report)
            
            # --- CHARTS ---
            st.subheader("📊 Price History")
            
            # Fetch data using our existing tool!
            ticker = user_input.upper()
            hist_1mo = get_historical_prices(ticker, "1mo")
            hist_1y = get_historical_prices(ticker, "1y")
            hist_3y = get_historical_prices(ticker, "3y")
            
            # Create 3 columns in the UI
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.caption("1 Month")
                if "error" not in hist_1mo:
                    st.line_chart(pd.Series(hist_1mo["closing_prices"]))
            with col2:
                st.caption("1 Year")
                if "error" not in hist_1y:
                    st.line_chart(pd.Series(hist_1y["closing_prices"]))
            with col3:
                st.caption("3 Years")
                if "error" not in hist_3y:
                    st.line_chart(pd.Series(hist_3y["closing_prices"]))
            
    # Save the agent's safe report to the UI memory
    st.session_state.chat_history.append({"role": "assistant", "content": safe_report})
