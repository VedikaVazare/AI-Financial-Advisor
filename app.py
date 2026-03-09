"""
Main Streamlit application entry point.
"""
import streamlit as st
import pandas as pd
from config import settings
from modules.financial_analyzer import FinancialAnalyzer
from modules.prompt_builder import PromptBuilder
from modules.visualizer import Visualizer
from utils.formatters import format_currency, format_percentage, format_months

# -----------------------------------------------------------------------------
# Configuration & Initialization
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS implementation
st.markdown("""
<style>
    .header-banner {
        background: linear-gradient(90deg, #1e3a5f 0%, #0d9488 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.1);
        text-align: center;
        background: #1e1e1e;
        color: white;
        margin-bottom: 1rem;
    }
    .metric-title { font-size: 1.1rem; color: #a1a1aa; }
    .metric-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
    .stMetric { border: 1px solid #333; padding: 1rem; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_groq_client():
    from modules.groq_client import GroqClient
    return GroqClient()

@st.cache_data(ttl=300)
def compute_metrics(income, expenses, savings, debt, emi):
    analyzer = FinancialAnalyzer(income, expenses, savings, debt, emi)
    return analyzer.calculate_metrics()

# Session State Initialization
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "advice" not in st.session_state:
    st.session_state.advice = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "expense_cats" not in st.session_state:
    st.session_state.expense_cats = {}

# Handle Missing Config
config_status = settings.validate_config()
if config_status["status"] == "error":
    st.error(f"Configuration Error: {config_status['message']}. Please check SETUP.md")

# -----------------------------------------------------------------------------
# Sidebar — User Input Panel
# -----------------------------------------------------------------------------
st.sidebar.title("📊 Your Financial Profile")

monthly_income = st.sidebar.number_input("Monthly Income (₹)", min_value=0.0, value=0.0, step=1000.0, help="Total monthly income after taxes")
monthly_expenses = st.sidebar.number_input("Monthly Expenses", min_value=0.0, value=0.0, step=500.0, help="Total monthly expenses excluding EMI")
monthly_emi = st.sidebar.number_input("Monthly EMI / Loan Payments (₹)", min_value=0.0, value=0.0, step=500.0, help="Total EMI commitments")
current_savings = st.sidebar.number_input("Current Savings", min_value=0.0, value=0.0, step=5000.0, help="Total liquid savings and investments")
total_debt = st.sidebar.number_input("Total Debt", min_value=0.0, value=0.0, step=10000.0, help="Total outstanding debt balance")

risk_appetite = st.sidebar.selectbox("Risk Appetite", options=["Conservative", "Moderate", "Aggressive"])
financial_goals = st.sidebar.text_area("Financial Goals", placeholder="e.g., Buy a house in 5 years, child's education, retirement at 55")

expense_categories = {}
with st.sidebar.expander("🗂️ Add Expense Categories (Optional)"):
    housing = st.number_input("Housing/Rent", min_value=0.0, step=500.0)
    food = st.number_input("Food & Groceries", min_value=0.0, step=500.0)
    transport = st.number_input("Transport", min_value=0.0, step=500.0)
    utilities = st.number_input("Utilities", min_value=0.0, step=500.0)
    entertainment = st.number_input("Entertainment", min_value=0.0, step=500.0)
    healthcare = st.number_input("Healthcare", min_value=0.0, step=500.0)
    education = st.number_input("Education", min_value=0.0, step=500.0)
    others = st.number_input("Others", min_value=0.0, step=500.0)
    
    total_cats = housing + food + transport + utilities + entertainment + healthcare + education + others
    if total_cats > 0:
        expense_categories = {
            "Housing/Rent": housing, "Food & Groceries": food, "Transport": transport,
            "Utilities": utilities, "Entertainment": entertainment, "Healthcare": healthcare,
            "Education": education, "Others": others
        }
        # Filter out 0 categories
        expense_categories = {k: v for k, v in expense_categories.items() if v > 0}
        
    if total_cats > monthly_expenses and monthly_expenses > 0:
        st.warning("Warning: Sum of categories exceeds total monthly expenses.")

if st.sidebar.button("🔍 Analyze My Finances", type="primary", use_container_width=True):
    if monthly_income == 0:
        st.sidebar.warning("Please enter a monthly income greater than 0.")
    else:
        if monthly_expenses + monthly_emi > monthly_income:
            st.sidebar.warning("Note: Your total expenses and EMIs exceed your income.")
            
        metrics = compute_metrics(monthly_income, monthly_expenses, current_savings, total_debt, monthly_emi)
        metrics['label'] = FinancialAnalyzer.get_health_label(metrics['financial_health_score'])
        
        st.session_state.metrics = metrics
        st.session_state.analyzed = True
        st.session_state.expense_cats = expense_categories
        st.session_state.user_profile = {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "current_savings": current_savings,
            "total_debt": total_debt,
            "monthly_emi": monthly_emi,
            "financial_goals": financial_goals,
            "risk_appetite": risk_appetite
        }
        
        # Reset specific states
        st.session_state.advice = None
        st.session_state.chat_history = []

# -----------------------------------------------------------------------------
# Main Panel
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-banner">
    <h1 style="margin:0; padding:0;">💰 AI Financial Advisor</h1>
    <p style="margin:0; padding:0; opacity:0.9;">Powered by Groq · llama-3.3-70b-versatile</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.analyzed:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 Financial Analysis\nGet a clear picture of your budget, savings rate, and overall financial health score.")
    with col2:
        st.markdown("### 🤖 AI Recommendations\nReceive personalized, actionable advice from an advanced AI modeled after top financial advisors.")
    with col3:
        st.markdown("### 📈 Visual Insights\nExplore interactive charts projecting your wealth growth and debt payoff timeline.")
    st.info("👈 Please fill in your financial profile in the sidebar and click 'Analyze My Finances' to begin.")

else:
    metrics = st.session_state.metrics
    profile = st.session_state.user_profile
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 AI Advice", "📈 Projections", "💬 Ask Advisor"])
    
    # -------------------------------------------------------------------------
    # Tab 1: Dashboard
    # -------------------------------------------------------------------------
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        score = metrics['financial_health_score']
        score_val = f"{score}/100"
        score_delta = "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Low"
        c1.metric("Health Score", score_val, delta=score_delta, delta_color="normal" if score >= 60 else "inverse")
        
        c2.metric("Savings Rate", format_percentage(metrics['savings_rate']), 
                 delta=f"{metrics['savings_rate']-20:.1f}% vs Target" if metrics['savings_rate'] else None,
                 delta_color="normal")
        
        c3.metric("Budget Ratio", format_percentage(metrics['budget_ratio']),
                 delta=f"{50-metrics['budget_ratio']:.1f}% vs Target" if metrics['budget_ratio'] else None,
                 delta_color="inverse") # Lower is better, but streamlits default green for + might be confusing here, so setting inverse
        
        c4.metric("Monthly Surplus", format_currency(metrics['monthly_surplus']),
                 delta="Positive" if metrics['monthly_surplus'] > 0 else "Negative",
                 delta_color="normal")
        
        # Row 2
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            donut_fig = Visualizer.create_budget_donut(
                profile['monthly_income'], profile['monthly_expenses'], 
                metrics['monthly_surplus'], profile['monthly_emi']
            )
            st.plotly_chart(donut_fig, use_container_width=True)
            
        with r2c2:
            gauge_fig = Visualizer.create_financial_gauge(score)
            st.plotly_chart(gauge_fig, use_container_width=True)
            
        # Row 3
        if profile['total_debt'] > 0:
            debt_fig = Visualizer.create_debt_payoff_chart(metrics['monthly_surplus'], profile['total_debt'])
            st.plotly_chart(debt_fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # Tab 2: AI Advice
    # -------------------------------------------------------------------------
    with tab2:
        try:
            client = get_groq_client()
            
            if st.session_state.advice is None:
                with st.spinner("🤖 Analyzing your finances... Please wait."):
                    prompt = PromptBuilder.build_analysis_prompt(profile, metrics)
                    stream = client.stream_financial_advice(prompt)
                    actionable_advice = st.write_stream(stream)
                    st.session_state.advice = actionable_advice
            else:
                st.markdown(st.session_state.advice)
                
            if st.session_state.advice:
                st.button("📋 Refresh Advice", on_click=lambda: st.session_state.pop("advice", None))
                escaped_advice = st.session_state.advice.replace('`','\\`').replace('$', '\\$')
                copy_js = f"""
                <script>
                function copyToClipboard() {{
                    const text = `{escaped_advice}`;
                    navigator.clipboard.writeText(text);
                    alert("Advice copied to clipboard!");
                }}
                </script>
                <button onclick="copyToClipboard()" style="padding:0.5rem 1rem; border-radius:4px; background:#4CAF50; color:white; border:none; cursor:pointer;">📋 Copy Advice</button>
                """
                st.components.v1.html(copy_js, height=50)
                
        except Exception as e:
            st.error(f"Failed to generate advice. Ensure API key is correct. Error: {str(e)}")

    # -------------------------------------------------------------------------
    # Tab 3: Projections
    # -------------------------------------------------------------------------
    with tab3:
        surplus = metrics['monthly_surplus']
        savings_fig = Visualizer.create_savings_growth_chart(max(0, surplus))
        st.plotly_chart(savings_fig, use_container_width=True)
        
        if st.session_state.expense_cats:
            exp_fig = Visualizer.create_expense_breakdown_bar(st.session_state.expense_cats)
            st.plotly_chart(exp_fig, use_container_width=True)
            
        st.markdown("### Projection Summary")
        summary_data = {
            "Metric": ["Current Savings", "Expected Annual Growth (Simple)", "Expected Debt Free In", "Monthly Emergency Capability"],
            "Value": [
                format_currency(profile['current_savings']),
                format_currency(max(0, surplus * 12)),
                format_months(metrics['debt_free_months']) if metrics['debt_free_months'] else "No Debt",
                f"{profile['current_savings'] / profile['monthly_expenses']:.1f} months" if profile['monthly_expenses'] > 0 else "N/A"
            ]
        }
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # Tab 4: Ask Advisor
    # -------------------------------------------------------------------------
    with tab4:
        st.markdown("### 💬 Chat with your AI Advisor")
        
        # Display chat history (limit visual rendering)
        display_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
        for msg in display_history:
            if msg["role"] != "system": 
                # Don't show the injected context to the user to keep the UI clean
                # Instead, check if parsing is needed
                content_to_show = msg["content"]
                if "User Question: " in content_to_show and msg["role"] == "user":
                    content_to_show = content_to_show.split("User Question: ")[-1]
                
                with st.chat_message(msg["role"]):
                    st.markdown(content_to_show)

        # Suggested Questions
        cols = st.columns(3)
        user_input = None
        if cols[0].button("How can I save more?"):
            user_input = "How can I save more?"
        elif cols[1].button("Best SIP for me?"):
            user_input = "What is the best SIP for me based on my risk profile?"
        elif cols[2].button("When will I be debt-free?"):
            user_input = "When will I be debt-free?"
        
        chat_val = st.chat_input("Ask a follow-up question...")
        if chat_val:
            user_input = chat_val

        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Prepare messages
            context = {
                "monthly_income": profile['monthly_income'],
                "monthly_expenses": profile['monthly_expenses'],
                "total_debt": profile['total_debt'],
                "current_savings": profile['current_savings'],
                "monthly_surplus": metrics['monthly_surplus']
            }
            
            system_content = "You are an expert, empathetic financial advisor helping a user with their personal finances in India."
            if not st.session_state.chat_history or st.session_state.chat_history[0]["role"] != "system":
                st.session_state.chat_history.insert(0, {"role": "system", "content": system_content})

            # Prepend financial context to message
            user_context = f"Financial Context:\\n- Monthly Income: ₹{context['monthly_income']:,}\\n- Monthly Expenses: ₹{context['monthly_expenses']:,}\\n- Total Debt: ₹{context['total_debt']:,}\\n- Savings: ₹{context['current_savings']:,}\\n- Surplus: ₹{context['monthly_surplus']:,}\\n\\nUser Question: {user_input}"
            
            st.session_state.chat_history.append({"role": "user", "content": user_context})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        client = get_groq_client()
                        response = client.chat(st.session_state.chat_history)
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error connecting to Advisor: {str(e)}")
