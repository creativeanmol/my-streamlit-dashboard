import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

# -------------------------------------------
# USER LOGIN SECTION
# -------------------------------------------
USER_CREDENTIALS = {
    "admin": "pass123",
    "anmol": "vachan2025"
}

def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "123":
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# In your main app flow
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    st.success("You are logged in!")
    
# -------------------------------------------
# MAIN DASHBOARD STARTS HERE
# -------------------------------------------

# Sidebar info
st.sidebar.success(f"👋 Welcome, {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

st.set_page_config(layout="wide")
st.title("🔍 Intraday Stock Scanner - Nifty 200")

# Nifty 200 symbols (truncated for demo; you can include full list)
NIFTY_200 = [
    "RELIANCE.NS", "ICICIBANK.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS",
    "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ITC.NS", "LT.NS"
]

# Fetch historical data
def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", auto_adjust=False, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        required = {'Open', 'High', 'Low', 'Close', 'Volume'}
        if df.empty or not required.issubset(df.columns):
            raise ValueError(f"{symbol} missing OHLCV")
        return df
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return pd.DataFrame()

# Calculate indicators
def calculate_indicators(df):
    try:
        df = df.dropna(subset=['Close'])
        df['EMA_9'] = EMAIndicator(close=df['Close'], window=9).ema_indicator()
        df['EMA_21'] = EMAIndicator(close=df['Close'], window=21).ema_indicator()
        df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()
        df['ATR'] = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14).average_true_range()
        df['TPV'] = df['Close'] * df['Volume']
        df['VWAP'] = df['TPV'].cumsum() / df['Volume'].cumsum()
        df.drop(columns=['TPV'], inplace=True)
        df['Price Change %'] = ((df['Close'] - df['Open']) / df['Open']) * 100
        df['Prev Close'] = df['Close'].shift(1)
        df['Gap %'] = ((df['Open'] - df['Prev Close']) / df['Prev Close']) * 100
        df['Vol Spike'] = df['Volume'] / df['Volume'].rolling(14).mean()
        return df
    except Exception as e:
        print(f"[INDICATORS ERROR] {e}")
        return pd.DataFrame()

# Score logic
def score_stock(df):
    if df.empty or len(df) < 1:
        return 0
    try:
        latest = df.iloc[-1]
        score = 0
        if latest['EMA_9'] > latest['EMA_21']:
            score += 1
        if latest['RSI'] < 30:
            score += 1
        if latest['Price Change %'] > 1:
            score += 1
        if latest['Vol Spike'] > 1.5:
            score += 1
        if latest['Close'] > latest['VWAP']:
            score += 1
        return score
    except Exception as e:
        print(f"[SCORE ERROR] {e}")
        return 0

# Analyze stocks
scored_stocks = []
progress = st.progress(0)
for idx, symbol in enumerate(NIFTY_200):
    progress.progress((idx + 1) / len(NIFTY_200))
    df = fetch_data(symbol)
    df = calculate_indicators(df)
    if df.empty:
        continue
    score = score_stock(df)
    scored_stocks.append({"symbol": symbol, "score": score, "data": df})

# Show top 10
top = sorted(scored_stocks, key=lambda x: x['score'], reverse=True)[:10]

st.subheader("🌟 Top 10 Intraday Candidates")
for item in top:
    st.write(f"**{item['symbol']}** - Score: {item['score']}")
    with st.expander(f"📈 Show Data for {item['symbol']}"):
        st.dataframe(item['data'].tail(10).style.format("{:.2f}"))

# Export
if top:
    export_df = pd.DataFrame([{"Symbol": s['symbol'], "Score": s['score']} for s in top])
    st.download_button("📂 Download Top Picks", export_df.to_csv(index=False), file_name="top_intraday_stocks.csv")
