
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Painel Bitget - BTC/USDT", layout="wide")
st.title("📊 Painel Bitget - Futuros BTC/USDT (USDT-M)")

def get_candles(symbol="BTCUSDT_UMCBL", granularity=60, limit=100):
    url = f"https://api.bitget.com/api/mix/v1/market/candles?symbol={symbol}&granularity={granularity}&limit={limit}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            return None
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume", "turnover"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
        df = df.sort_values("timestamp")
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        return df
    except Exception as e:
        st.warning(f"Erro ao obter candles ({symbol}, {granularity}): {e}")
        return None

def display_block(df, title):
    if df is None or df.empty:
        st.warning(f"Nenhum dado carregado para {title}")
        return

    last_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2] if len(df) > 1 else last_close
    pct_change = (last_close - prev_close) / prev_close * 100 if prev_close else 0
    pct_icon = "🔺" if pct_change > 0 else "🔻"

    rsi = compute_rsi(df["close"])
    macd_signal = compute_macd(df["close"])
    bb_info = compute_bollinger(df["close"])

    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 6])
    col1.metric(f"📈 {title}", f"${last_close:,.2f}", f"{pct_icon}{pct_change:.2f}%")
    col2.write(f"**RSI:** {rsi:.1f}" if rsi else "RSI: N/A")
    col3.write(f"**MACD:** {macd_signal}" if macd_signal else "MACD: N/A")
    col4.write(f"**BB:** {bb_info}" if bb_info else "BB: N/A")
    col5.write("")
    col6.write(f"📊 _Análise técnica automatizada para {title}_")

def compute_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(period).mean()
    ma_down = down.rolling(period).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.isnull().all() else None

def compute_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return "Alta" if macd.iloc[-1] > signal.iloc[-1] else "Baixa"

def compute_bollinger(series, window=20):
    ma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    if series.iloc[-1] < lower.iloc[-1]:
        return "Abaixo da banda inferior"
    elif series.iloc[-1] > upper.iloc[-1]:
        return "Acima da banda superior"
    else:
        return "Dentro das bandas"

# Atualização
st.caption(f"🕒 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Bloco técnico para 1H, 4H, 1D
timeframes = {
    "1H": 60,
    "4H": 240,
    "1D": 1440
}

for label, granularity in timeframes.items():
    df = get_candles(granularity=granularity)
    display_block(df, label)

# Preço atual
st.subheader("📉 Preços em tempo real (Futuros USDT-M)")
ticker_url = "https://api.bitget.com/api/mix/v1/market/ticker?symbol=BTCUSDT_UMCBL&productType=umcbl"
try:
    resp = requests.get(ticker_url, timeout=5)
    price_now = float(resp.json()["data"]["last"])
    st.metric("BTC/USDT", f"${price_now:,.2f}")
except:
    st.error("Erro: Dados de 1H estão vazios. Verifique a API ou a resposta da Bitget.")
    st.subheader("💰 Preço Atual BTC/USDT: N/D")
