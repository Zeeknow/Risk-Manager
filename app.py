import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Crypto Risk Ledger", page_icon="📊", layout="centered")
st.title("Crypto Risk Manager & Trade Ledger")

# --- SIDEBAR: Dynamic Capital & Risk Controls ---
st.sidebar.header("⚙️ Account Settings")

default_capital = st.sidebar.number_input(
    "Starting Capital (₦)", 
    min_value=1000.0, 
    value=200000.0, 
    step=10000.0
)
risk_pct = st.sidebar.number_input(
    "Risk Per Trade (%)", 
    min_value=0.1, 
    max_value=10.0, 
    value=1.0, 
    step=0.5
) / 100.0

daily_limit_pct = st.sidebar.number_input(
    "Daily Loss Limit (%)", 
    min_value=1.0, 
    max_value=20.0, 
    value=3.0, 
    step=1.0
) / 100.0

# Initialize session state variables
if "balance" not in st.session_state:
    st.session_state.balance = default_capital
if "trades" not in st.session_state:
    st.session_state.trades = []

# Reset / Sync Balance button in sidebar
if st.sidebar.button("Reset / Sync Capital"):
    st.session_state.balance = default_capital
    st.session_state.trades = []
    st.rerun()

# --- CALCULATIONS ---
today_str = str(date.today())
today_pnl = sum(t["PnL (₦)"] for t in st.session_state.trades if t["Date"] == today_str)

current_risk_amount = st.session_state.balance * risk_pct
daily_loss_limit = st.session_state.balance * daily_limit_pct

# --- METRICS & ALERTS ---
col1, col2 = st.columns(2)
col1.metric("Account Balance", f"₦{st.session_state.balance:,.2f}")
col2.metric("Today's PnL", f"₦{today_pnl:,.2f}")

if today_pnl <= -daily_loss_limit:
    st.error(f"🚨 CIRCUIT BREAKER TRIGGERED! You hit your daily loss limit of ₦{daily_loss_limit:,.2f}. Stop trading for 24 hours.")
elif today_pnl <= -(daily_loss_limit * 0.66):
    st.warning(f"⚠️ Approaching daily limit (₦{daily_loss_limit:,.2f} max loss). Reduce position size!")
else:
    st.success(f"🟢 Safe to trade. Maximum risk per trade: ₦{current_risk_amount:,.2f} ({risk_pct*100:.1f}%).")

st.divider()

# --- TRADE INPUT FORM ---
st.subheader("Log New Trade Outcome")
with st.form("trade_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    pair = col_a.text_input("Pair", "BTC/USDT")
    side = col_b.selectbox("Side", ["Long", "Short"])
    pnl = st.number_input("Outcome PnL in NGN (+ for win, - for loss)", value=0.0, step=500.0)
    
    if st.form_submit_button("Submit Trade"):
        st.session_state.balance += pnl
        st.session_state.trades.append({
            "Date": today_str,
            "Pair": pair,
            "Side": side,
            "PnL (₦)": pnl,
            "Updated Balance (₦)": st.session_state.balance
        })
        st.success("Trade logged successfully!")
        st.rerun()

# --- LEDGER HISTORY ---
st.subheader("Trade Ledger History")
if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No trades logged yet.")