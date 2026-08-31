import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# Page Config (Mobile Responsive & Dark Mode)
st.set_page_config(page_title="StockEzee Pro", layout="wide")

# Custom Dark Styling
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div.stButton > button { width: 100%; background-color: #00D09C; color: black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("⚡ StockEzee - Live Screener")

# Stockezee Jaisa Navigation Menu
menu = st.sidebar.radio("Navigation", ["📈 Home / Stocks", "⚡ Intraday Booster", "📊 Sector Booster", "🎯 Stock Screener"])

# 1. HOME & STOCKS SEARCH
if menu == "📈 Home / Stocks":
    st.subheader("🔍 Stock Search & Technical Analysis")
    symbol = st.text_input("NSE Symbol Likhein (e.g., RELIANCE.NS, TATAMOTORS.NS, NIFTY):", "RELIANCE.NS")
    
    if symbol:
        df = yf.download(symbol, period="5d", interval="15m")
        if not df.empty:
            # Flatten columns if multi-index
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            last_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change = last_price - prev_close
            p_change = (change / prev_close) * 100
            
            col1, col2 = st.columns(2)
            col1.metric("Live Price", f"₹{round(last_price, 2)}", f"{round(p_change, 2)}%")
            
            # Technical Indicators
            df['RSI'] = df.ta.rsi(length=14)
            st.write(f"**Current RSI (14):** {round(df['RSI'].iloc[-1], 2)}")
            st.line_chart(df['Close'])

# 2. INTRADAY BOOSTER
elif menu == "⚡ Intraday Booster":
    st.subheader("⚡ Intraday High Probability Setups")
    st.caption("RSI > 55 aur MACD Bullish Crossover wale stocks:")
    
    watchlist = ["RELIANCE.NS", "TATAMOTORS.NS", "SBIN.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS", "HDFCBANK.NS"]
    booster_list = []
    
    for stock in watchlist:
        df = yf.download(stock, period="5d", interval="15m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df['RSI'] = df.ta.rsi(length=14)
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            df['MACD'] = macd['MACD_12_26_9']
            df['Signal'] = macd['MACDs_12_26_9']
            
            latest = df.iloc[-1]
            rsi_val = round(latest['RSI'], 2)
            price = round(latest['Close'], 2)
            
            if rsi_val > 55 and latest['MACD'] > latest['Signal']:
                booster_list.append({"Stock": stock.replace(".NS",""), "Price": price, "RSI": rsi_val, "Signal": "🔥 BULLISH"})
            elif rsi_val < 45 and latest['MACD'] < latest['Signal']:
                booster_list.append({"Stock": stock.replace(".NS",""), "Price": price, "RSI": rsi_val, "Signal": "🔻 BEARISH"})

    if booster_list:
        st.dataframe(pd.DataFrame(booster_list), use_container_width=True)
    else:
        st.info("Filhaal koi strong momentum booster setup nahi mil raha hai.")

# 3. SECTOR BOOSTER
elif menu == "📊 Sector Booster":
    st.subheader("📊 Key Sector Performance")
    sectors = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Nifty IT": "^CNXIT"}
    
    sec_data = []
    for sec_name, sec_symbol in sectors.items():
        data = yf.download(sec_symbol, period="2d", interval="1d", progress=False)
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            close = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2]
            chg = round(((close - prev)/prev)*100, 2)
            sec_data.append({"Sector": sec_name, "Price": round(close, 2), "Change %": f"{chg}%"})
            
    st.table(sec_data)

# 4. STOCK SCREENER
elif menu == "🎯 Stock Screener":
    st.subheader("🎯 Auto Stock Screener")
    min_rsi = st.slider("Filter Minimum RSI:", 30, 70, 50)
    
    stocks = ["BHARTIARTL.NS", "ASHOKA.NS", "ZEEL.NS", "YESBANK.NS", "TCS.NS", "SBIN.NS"]
    screen_results = []
    
    for s in stocks:
        df = yf.download(s, period="2d", interval="15m", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            rsi = df.ta.rsi(length=14).iloc[-1]
            price = df['Close'].iloc[-1]
            if rsi >= min_rsi:
                screen_results.append({"Stock": s.replace(".NS",""), "Price (₹)": round(price,2), "RSI": round(rsi,2)})
                
    st.dataframe(pd.DataFrame(screen_results), use_container_width=True)
