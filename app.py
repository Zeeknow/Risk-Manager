import streamlit as st  # type: ignore[import-not-found]
import pandas as pd
from datetime import date

st.set_page_config(page_title="Crypto Risk Ledger", page_icon="📊", layout="centered")
st.title("₦200k Risk Manager & Trade Ledger")

# Persistent state initialization
if "balance" not in st.session_state:
    st.session_state.balance = 200000.0
if "trades" not in st.session_state:
    st.session_state.trades = []

# Top Summary Metrics
today_str = str(date.today())
today_pnl = sum(t["PnL (₦)"] for t in st.session_state.trades if t["Date"] == today_str)

col1, col2 = st.columns(2)
col1.metric("Account Balance", f"₦{st.session_state.balance:,.2f}")
col2.metric("Today's PnL", f"₦{today_pnl:,.2f}")

# Circuit Breaker Banner
if today_pnl <= -6000:
    st.error("🚨 CIRCUIT BREAKER TRIGGERED! You have lost ₦6,000 today. Stop trading for 24 hours.")
elif today_pnl <= -4000:
    st.warning("⚠️ Approaching daily limit. Only ₦2,000 drawdown left for today.")
else:
    st.success("🟢 Safe to trade. Stick to ₦2,000 risk per trade.")

st.divider()

# Trade Input Form
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
        st.success("Trade logged!")
        st.rerun()

# History Ledger
st.subheader("Trade Ledger History")
if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No trades logged in this session yet.")