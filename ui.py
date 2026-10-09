import streamlit as st
from agent import build_team

# 1. Web Page Setup
st.set_page_config(page_title="Financial Agent UI", page_icon="📈", layout="centered")

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
            
            # CRITICAL BUG FIX: 
            # Streamlit interprets text between two '$' signs as LaTeX Math.
            # So a sentence like "$100 to $200" turns into an ugly math formula!
            # We fix this by escaping the dollar signs before rendering.
            safe_report = report.replace("$", r"\$")
            
            # Show the report
            st.markdown(safe_report)
            
    # Save the agent's safe report to the UI memory
    st.session_state.chat_history.append({"role": "assistant", "content": safe_report})
