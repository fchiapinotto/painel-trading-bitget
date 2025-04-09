import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Painel Bitget - Futuros BTC/USDT (1H)")

# Atualização
st.caption(f"🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# === Consulta à API da Bitget ===
url = "https://api.bitget.com/api/v2/mix/market/candles"
params = {
    "symbol": "BTCUSDT",
    "productType": "USDT-FUTURES",
    "granularity": "60",
    "limit": 100
}

try:
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    raw_data = r.json()["data"]

    # Processar os dados em um DataFrame
    df = pd.DataFrame(raw_data, columns=["timestamp", "open", "high", "low", "close", "volume", "quoteVolume"])
    
    df["startTime"] = pd.to_datetime(df["startTime"], unit="ms")
    df["endTime"] = pd.to_datetime(df["endTime"], unit="ms")

df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df = df.sort_values("timestamp")

    # Cálculo dos indicadores técnicos
    df["MA20"] = df["close"].rolling(window=20).mean()
    df["STD20"] = df["close"].rolling(window=20).std()
    df["Upper"] = df["MA20"] + 2 * df["STD20"]
    df["Lower"] = df["MA20"] - 2 * df["STD20"]

    delta = ((df["close"].iloc[-1] - df["close"].iloc[-2]) / df["close"].iloc[-2]) * 100
    rsi = 100 - (100 / (1 + (df["close"].diff().clip(lower=0).rolling(window=14).mean() / 
                            df["close"].diff().clip(upper=0).abs().rolling(window=14).mean())))
    macd_line = df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean()

    # === Exibir card com dados atuais ===
    st.subheader("📌 Indicadores Atuais")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Valor Atual", f"${df['close'].iloc[-1]:,.2f}", f"{delta:.2f}%")
    col2.metric("RSI", f"{rsi.iloc[-1]:.2f}")
    col3.metric("MACD", f"{macd_line.iloc[-1]:.2f}")
    col4.metric("BB Sup", f"{df['Upper'].iloc[-1]:,.2f}")
    col5.metric("BB Inf", f"{df['Lower'].iloc[-1]:,.2f}")

    # === Plot do gráfico ===
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candles"
    ))

    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["Upper"], mode="lines", name="BB Superior",
                             line=dict(color="blue", width=1, dash="dot")))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["MA20"], mode="lines", name="BB Média",
                             line=dict(color="blue", width=1)))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["Lower"], mode="lines", name="BB Inferior",
                             line=dict(color="red", width=1, dash="dot")))

    fig.update_layout(
        title="BTC/USDT (1H) com Bollinger Bands",
        xaxis_title="Hora",
        yaxis_title="Preço",
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("Erro ao carregar dados da API Bitget.")
    st.exception(e)
