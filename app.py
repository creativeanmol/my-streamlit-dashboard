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
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
            st.stop()  # Prevent further execution
        else:
            st.error("Invalid credentials")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

# Show login page if not logged in
if not st.session_state["logged_in"]:
    login()
    st.stop()  # 👈 Prevent dashboard from running

# -------------------------------------------
# MAIN DASHBOARD STARTS HERE
# -------------------------------------------
st.set_page_config(layout="wide")
st.sidebar.success(f"👋 Welcome, {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

st.title("🔍 Intraday Stock Scanner - Nifty 200")
# Nifty 200 symbols (truncated for demo; you can include full list)
NIFTY_200 = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LT.NS", "SBIN.NS", "AXISBANK.NS",
    "ITC.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "HCLTECH.NS", "ASIANPAINT.NS",
    "WIPRO.NS", "MARUTI.NS", "DMART.NS", "SUNPHARMA.NS", "TITAN.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ADANIPOWER.NS", "ADANITRANS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "ONGC.NS", "COALINDIA.NS",
    "BPCL.NS", "IOC.NS", "GAIL.NS", "NTPC.NS", "POWERGRID.NS", "TECHM.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS",
    "BAJAJFINSV.NS", "HDFCLIFE.NS", "ICICIPRULI.NS", "SBILIFE.NS", "ULTRACEMCO.NS", "SHREECEM.NS", "GRASIM.NS",
    "NESTLEIND.NS", "BRITANNIA.NS", "M&M.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "INDUSINDBK.NS",
    "HINDALCO.NS", "VEDL.NS", "ZOMATO.NS", "PAYTM.NS", "POLYCAB.NS", "RVNL.NS", "IRFC.NS", "IRCTC.NS", "LTIM.NS",
    "LTTS.NS", "BEL.NS", "BHEL.NS", "INDIGO.NS", "PNB.NS", "BANKBARODA.NS", "IDFCFIRSTB.NS", "UNIONBANK.NS",
    "CANBK.NS", "FEDERALBNK.NS", "YESBANK.NS", "AUROPHARMA.NS", "BIOCON.NS", "LUPIN.NS", "ABB.NS", "SIEMENS.NS",
    "TATAPOWER.NS", "INDUSTOWER.NS", "JINDALSTEL.NS", "SJVN.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "AMBUJACEM.NS",
    "ACC.NS", "DABUR.NS", "PIDILITIND.NS", "COLPAL.NS", "GODREJCP.NS", "HAVELLS.NS", "VOLTAS.NS", "PAGEIND.NS",
    "TRENT.NS", "TATACONSUM.NS", "UBL.NS", "PETRONET.NS", "MOTHERSUMI.NS", "MCDOWELL-N.NS", "INDIAMART.NS",
    "NAUKRI.NS", "AFFLE.NS", "DEEPAKNTR.NS", "AARTIIND.NS", "BALRAMCHIN.NS", "BALKRISIND.NS", "CHAMBLFERT.NS",
    "COROMANDEL.NS", "RALLIS.NS", "TATACHEM.NS", "TATAELXSI.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS",
    "KPITTECH.NS", "ZYDUSLIFE.NS", "GLENMARK.NS", "TORNTPHARM.NS", "IPCALAB.NS", "ALKEM.NS", "APOLLOHOSP.NS",
    "FORTIS.NS", "MAXHEALTH.NS", "ICICIGI.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS", "HDFCAMC.NS",
    "MOTILALOFS.NS", "IIFL.NS", "BAJAJHLDNG.NS", "RECLTD.NS", "POWERFIN.NS", "PFC.NS", "CONCOR.NS", "NHPC.NS",
    "NLCINDIA.NS", "HINDCOPPER.NS", "MOIL.NS", "NMDC.NS", "SAIL.NS", "TATACOMM.NS", "IDEA.NS", "INDHOTEL.NS",
    "EIHOTEL.NS", "LEMONTREE.NS", "CESC.NS", "APOLLOTYRE.NS", "CEATLTD.NS", "MRF.NS", "JKTYRE.NS", "RAMCOCEM.NS",
    "JKCEMENT.NS", "FIVESTAR.NS", "SYRMA.NS", "RAJRATAN.NS", "KEI.NS", "FINCABLES.NS", "CGPOWER.NS", "TRIVENI.NS",
    "SPARC.NS", "PNCINFRA.NS", "PNBGILTS.NS", "TEXRAIL.NS", "KNRCON.NS", "GRINFRA.NS", "IRB.NS", "HGINFRA.NS",
    "LAURUSLABS.NS", "GNFC.NS", "TATAMETALI.NS", "KALYANKJIL.NS", "SOBHA.NS", "OBEROIRLTY.NS", "LODHA.NS",
    "BRIGADE.NS", "PRESTIGE.NS", "GMRINFRA.NS", "ADANIGAS.NS", "IGL.NS", "MAHSEAMLES.NS", "MAHINDCIE.NS",
    "JUBLFOOD.NS", "DELHIVERY.NS", "SCHAEFFLER.NS", "BATAINDIA.NS", "RELAXO.NS", "CROMPTON.NS", "BAJAJELEC.NS",
    "TIINDIA.NS", "SCHNEIDER.NS", "ABBOTINDIA.NS", "PFIZER.NS", "SANOFI.NS", "BBTC.NS", "NAVINFLUOR.NS",
    "SRF.NS", "PIIND.NS", "VINATIORGA.NS", "AUBANK.NS", "RBLBANK.NS", "CREDITACC.NS", "EDELWEISS.NS",
    "SHRIRAMFIN.NS", "UGROCAP.NS", "CAMS.NS", "SFL.NS", "IEX.NS", "MCX.NS", "BSE.NS", "CENTURYTEX.NS",
    
    # Additional intraday picks
    "TATVA.NS", "IRB.NS", "CLEAN.NS", "FLUOROCHEM.NS", "BLS.NS", "IDEAFORGE.NS", "KFINTECH.NS",
    "JIOFIN.NS", "MAZDOCK.NS", "GICRE.NS", "IIFLWAM.NS", "GRSE.NS", "ELECTCAST.NS", "VISHNU.NS",
    "TMB.NS", "RITES.NS", "CARYSIL.NS", "SURYAROSNI.NS", "GOKEX.NS"
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

# -------------------------------------------
# SCORING LOGIC
# -------------------------------------------
def score_stock(df):
    if df.empty or len(df) < 1:
        return 0, None, "Insufficient Data"
    try:
        latest = df.iloc[-1]
        score = 0
        buy_price = None
        profit_signals = 0

        if latest['EMA_9'] > latest['EMA_21']:
            score += 1
            profit_signals += 1
        if 40 < latest['RSI'] < 70:
            score += 1
            profit_signals += 1
        if latest['Price Change %'] > 1:
            score += 1
            profit_signals += 1
        if latest['Vol Spike'] > 1.5:
            score += 1
            profit_signals += 1
        if latest['Close'] > latest['VWAP']:
            score += 1
            profit_signals += 1

        if score >= 3:
            buy_price = round(float(latest['Close']), 2)

        label = "Probable Profit ✅" if profit_signals >= 4 else "Risky ⚠️"

        return score, buy_price, label
    except Exception as e:
        print(f"[SCORE ERROR] {e}")
        return 0, None, "Error"

# -------------------------------------------
# ANALYZE & RANK STOCKS
# -------------------------------------------
scored_stocks = []
progress = st.progress(0)
for idx, symbol in enumerate(NIFTY_200):
    progress.progress((idx + 1) / len(NIFTY_200))
    df = fetch_data(symbol)
    df = calculate_indicators(df)
    if df.empty:
        continue
    score, buy_price, label = score_stock(df)
    scored_stocks.append({
        "symbol": symbol,
        "score": score,
        "buy_price": buy_price,
        "label": label,
        "data": df
    })

# -------------------------------------------
# DISPLAY TOP 10 RESULTS
# -------------------------------------------
top = sorted(scored_stocks, key=lambda x: x['score'], reverse=True)[:10]
st.subheader("🌟 Top 10 Intraday Candidates")
for item in top:
    st.write(
        f"**{item['symbol']}** - Score: {item['score']} | 🎯 Buy Price: {item['buy_price'] or 'N/A'} | 📈 Outcome: {item['label']}"
    )
    with st.expander(f"📈 Show Data for {item['symbol']}"):
        st.dataframe(item['data'].tail(10).style.format("{:.2f}"))

# -------------------------------------------
# EXPORT CSV
# -------------------------------------------
if top:
    export_df = pd.DataFrame([
        {
            "Symbol": s['symbol'],
            "Score": s['score'],
            "Buy Price": s['buy_price'],
            "Outcome": s['label']
        } for s in top
    ])
    st.download_button("📂 Download Top Picks", export_df.to_csv(index=False), file_name="top_intraday_stocks.csv")
