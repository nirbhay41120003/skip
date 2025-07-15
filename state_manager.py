import streamlit as st
from ledger_manager import LedgerManager

class StateManager:
    def __init__(self):
        if 'ledger_manager' not in st.session_state:
            st.session_state.ledger_manager = LedgerManager()
            self.load_sample_data()
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            self.add_welcome_message()
        
        if 'current_language' not in st.session_state:
            st.session_state.current_language = "hi"
    
    def add_welcome_message(self):
        welcome_message = """
        नमस्ते! मैं आपका AI व्यापार सहायक हूं। मुझसे अपने व्यापार के बारे में कुछ भी पूछें जैसे:
        • "इस हफ्ते के खर्च क्या हैं?"
        • "किसका पैसा बाकी है?"
        • "त्योहार के लिए ऑफर मैसेज बनाओ"
        """
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": welcome_message
        })
    
    def load_sample_data(self):
        lm = st.session_state.ledger_manager
        lm.add_transaction("राम कुमार", 1500, "credit", "दूध की बिक्री")
        lm.add_transaction("श्याम", 500, "debit", "सामान खरीदा")
    
    def add_chat_message(self, role, content):
        st.session_state.chat_history.append({
            "role": role,
            "content": content
        })