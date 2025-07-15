import streamlit as st
from datetime import datetime
from gemini_integration import GeminiIntegration
from state_manager import StateManager

# Initialize state manager
state_manager = StateManager()

# Initialize Gemini integration
gemini = GeminiIntegration(st.secrets["GEMINI_API_KEY"])

# App title and description
st.title("🧮 AI-Khata")
st.subheader("Smart Business Management for Indian SMBs")

# Tabs for navigation
tab1, tab2 = st.tabs(["🧠 AI Assistant", "📒 Manual Ledger"])

with tab1:
    st.header("🤖 AI Business Assistant")
    st.caption("Ask me anything about your business in English or Hindi")
    
    # Language selector
    languages = {
        "en": "English",
        "hi": "हिन्दी",
        "bn": "বাংলা",
        "ta": "தமிழ்",
        "te": "తెలుగు",
        "mr": "मराठी",
        "gu": "ગુજરાતી",
        "kn": "ಕನ್ನಡ",
        "ml": "മലയാളം",
        "pa": "ਪੰਜਾਬੀ",
        "or": "ଓଡ଼ିଆ"
    }
    selected_lang = st.selectbox("Select Language", options=list(languages.keys()), 
                                format_func=lambda x: languages[x])
    
    # Chat history display
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
    
    # Chat input
    user_input = st.chat_input("Type your question here...")
    if user_input:
        state_manager.add_chat_message("user", user_input)
        
        # Build context for Gemini
        lm = st.session_state.ledger_manager
        insights = lm.generate_business_insights()
        context = f"""
        BUSINESS CONTEXT:
        - Total Balance: ₹{insights['total_balance']:,.2f}
        - Total Sales: ₹{insights['total_sales']:,.2f}
        - Total Expenses: ₹{insights['total_expenses']:,.2f}
        - Net Profit: ₹{insights['net_profit']:,.2f}
        - Top Customers: {', '.join([c['name'] for c in insights['top_customers']])}
        """
        
        # Get Gemini response
        with st.spinner("Thinking..."):
            response = gemini.generate_response(
                user_input, 
                f"You are an AI business assistant. Respond in {languages[selected_lang]}." + context
            )
        
        state_manager.add_chat_message("assistant", response)
        st.rerun()

with tab2:
    st.header("📒 Manual Ledger")
    
    # Balance card
    lm = st.session_state.ledger_manager
    total_balance = lm.calculate_total_balance()
    st.subheader(f"Total Balance: ₹{total_balance:,.2f}")
    
    # Add transaction form
    with st.form("add_transaction"):
        st.subheader("Add New Transaction")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            transaction_type = st.selectbox("Type", [
                "Credit (उधार दिया)",
                "Debit (उधार लिया)",
                "Sale (बिक्री)",
                "Expense (खर्च)"
            ])
            # Map to internal types
            type_map = {
                "Credit (उधार दिया)": "credit",
                "Debit (उधार लिया)": "debit",
                "Sale (बिक्री)": "sale",
                "Expense (खर्च)": "expense"
            }
            transaction_type_code = type_map[transaction_type]
        
        with col2:
            customer_name = st.text_input("Customer/Party", placeholder="Customer name")
        
        with col3:
            transaction_date = st.date_input("Date", datetime.now())
        
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
        description = st.text_area("Description", placeholder="Transaction details...")
        
        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            if not customer_name or amount <= 0:
                st.error("Please fill in all required fields")
            else:
                lm.add_transaction(
                    customer_name,
                    amount,
                    transaction_type_code,
                    description,
                    created_at=datetime.combine(transaction_date, datetime.min.time()).isoformat()
                )
                st.success("Transaction added successfully!")
                st.rerun()
    
    # Filters
    st.subheader("Transaction History")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filter_type = st.selectbox("Filter by Type", [
            "All", "Credit", "Debit", "Sale", "Expense"
        ], index=0)
    with col2:
        filter_from = st.date_input("From Date", value=None)
    with col3:
        filter_to = st.date_input("To Date", value=None)
    with col4:
        filter_customer = st.text_input("Customer", placeholder="Customer name")
    
    # Apply filters
    filtered_transactions = lm.get_filtered_transactions(
        transaction_type=filter_type,
        start_date=filter_from,
        end_date=filter_to,
        customer_name=filter_customer
    )
    
    # Display transactions
    if not filtered_transactions:
        st.info("No transactions found")
    else:
        for t in filtered_transactions:
            amount_display = f"₹{abs(t.amount):,.2f}"
            if t.amount < 0:
                amount_display = f"-₹{abs(t.amount):,.2f}"
            
            with st.expander(f"{t.customer_name} - {amount_display}"):
                st.write(f"**Type:** {t.type.capitalize()}")
                st.write(f"**Date:** {datetime.fromisoformat(t.created_at).strftime('%d/%m/%Y')}")
                st.write(f"**Description:** {t.description}")
    
    # Export/Import
    st.divider()
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Data"):
            export_filename = f"ai_khata_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            lm.export_data(export_filename)
            with open(export_filename, "rb") as f:
                st.download_button(
                    label="Download Export",
                    data=f,
                    file_name=export_filename,
                    mime="application/json"
                )
    
    with col2:
        uploaded_file = st.file_uploader("Import Data", type=["json"])
        if uploaded_file is not None:
            import_filename = f"ai_khata_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(import_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            lm.import_data(import_filename)
            st.success("Data imported successfully!")
            st.rerun()

# Add keyboard shortcuts
st.markdown("""
<style>
    .stApp [data-testid="stDecoration"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)