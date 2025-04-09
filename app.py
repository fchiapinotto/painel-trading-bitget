
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import requests
import datetime

# === Função para obter candles diretamente da API da Bitget ===
def fetch_bitget_candles(symbol="BTCUSDT_UMCBL", interval="60", limit=100):
    url = f"https://api.bitget.com/api/mix/v1/market/candles?symbol={symbol}&granularity={interval}&limit={limit}&productType=umcbl"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "quoteVolume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
        return df.sort_values("timestamp")
    else:
        return pd.DataFrame()

# === Funções de indicadores ===
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger(series, window=20, num_std=2):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + num_std * std
    lower_band = sma - num_std * std
    return upper_band, sma, lower_band

# === App Streamlit ===
st.set_page_config(layout="wide")
st.title("📊 Painel Bitget - Futuros BTC/USDT (1H)")

# Atualização
st.markdown(f"🕒 Atualizado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# === Carregar dados da API ===
df = fetch_bitget_candles()

if df.empty:
    st.error("Erro ao carregar dados da API Bitget.")
else:
    # === Indicadores ===
    rsi = calculate_rsi(df["close"])
    macd_line, signal_line = calculate_macd(df["close"])
    upper_bb, mid_bb, lower_bb = calculate_bollinger(df["close"])

    # === Exibir Card superior ===
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Preço Atual", f"${df['close'].iloc[-1]:,.2f}")
    with col2:
        pct_change = ((df["close"].iloc[-1] - df["close"].iloc[-2]) / df["close"].iloc[-2]) * 100
        st.metric("Variação 1H", f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
    with col3:
        st.metric("RSI", f"{rsi.iloc[-1]:.2f}")
    with col4:
        st.metric("MACD", f"{macd_line.iloc[-1] - signal_line.iloc[-1]:.2f}")
    with col5:
        st.metric("BB Inferior", f"{lower_bb.iloc[-1]:,.2f}")

    # === Gráfico interativo ===
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="Candles"
    ))

    fig.add_trace(go.Scatter(x=df["timestamp"], y=upper_bb, mode="lines", name="BB Superior", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=mid_bb, mode="lines", name="BB Média"))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=lower_bb, mode="lines", name="BB Inferior", line=dict(dash="dot")))

    fig.update_layout(
        title="BTC/USDT (1H) com Bollinger Bands",
        xaxis_title="Hora",
        yaxis_title="Preço",
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
