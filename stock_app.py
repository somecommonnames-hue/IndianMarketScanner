import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import sqlite3
import datetime

def get_nifty_data(interval="1m"):
    ticker = yf.Ticker("^NSEI")
    df = ticker.history(period="1d", interval=interval)
    return df

def compute_indicators(df):
    df["RSI"] = ta.rsi(df["Close"])
    macd = ta.macd(df["Close"])
    if macd is not None:
        df["MACD"] = macd["MACD_12_26_9"]
        df["MACD_signal"] = macd["MACDs_12_26_9"]
    else:
        df["MACD"] = None
        df["MACD_signal"] = None
    df["WilliamsR"] = ta.willr(df["High"], df["Low"], df["Close"])
    return df.tail(10)

def log_trade(symbol, entry, target, strategy):
    conn = sqlite3.connect("tradelog.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            date TEXT, symbol TEXT, entry REAL, target REAL, strategy TEXT, status TEXT
        )
    """)
    cursor.execute("INSERT INTO trades VALUES (?,?,?,?,?,?)",
                   (str(datetime.datetime.now()), symbol, entry, target, strategy, "Open"))
    conn.commit()
    conn.close()

def get_trade_logs():
    conn = sqlite3.connect("tradelog.db")
    df = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()
    return df

st.title("📈 Indian Stock Market Multi-Strategy Scanner")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Nifty Intraday", "Options Scalping", "Swing Trading", "Positional", "ETF", "Trade Logs"]
)

with tab1:
    st.subheader("Nifty Trend & Intraday Analysis")
    df = get_nifty_data()
    indicators = compute_indicators(df)
    st.dataframe(indicators)

with tab2:
    st.subheader("Options Scalping Opportunities (3-Min Strategy)")
    st.table(pd.DataFrame({
        "Strike": [22200, 22100],
        "Type": ["CE", "PE"],
        "Entry": [120, 95],
        "Target": [135, 110],
        "Stop-loss": [110, 85],
        "Probability": ["78%", "72%"]
    }))

with tab3:
    st.subheader("Swing Trading Scanner (1–2 Weeks)")
    st.table(pd.DataFrame({
        "Stock": ["HDFC Bank", "Reliance"],
        "Sector": ["Financials", "Energy"],
        "Entry": ["1450–1470", "2400–2420"],
        "Target": ["1600", "2600"],
        "Indicators": ["RSI↑, MACD+, Vol Spike", "RSI↑, Williams %R > -20"]
    }))

with tab4:
    st.subheader("Positional Trading Scanner (1–2 Months)")
    st.table(pd.DataFrame({
        "Stock": ["Infosys", "Tata Steel"],
        "Sector": ["IT", "Metals"],
        "Entry": ["1350–1370", "120–125"],
        "Target": ["1600", "150"],
        "Signals": ["EMA 50>200, MACD+, ORB", "Elliott Wave 3, RSI↑"]
    }))

with tab5:
    st.subheader("ETF Positional Opportunities")
    st.table(pd.DataFrame({
        "ETF": ["Nifty BeES", "Bank BeES"],
        "Entry": ["230–232", "350–355"],
        "Target": ["245", "370"],
        "Trend": ["Bullish", "Bullish"]
    }))

with tab6:
    st.subheader("Central Trade Log")
    if st.button("Log Sample Trade"):
        log_trade("NIFTY", 22000, 22500, "Swing")
    logs = get_trade_logs()
    st.dataframe(logs)
