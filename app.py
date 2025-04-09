
mport streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Painel BTC/USDT", layout="wide")
st.title("📈 Painel Bitget - Futuros BTC/USDT")

st.caption(f"🕒 Atualizado em: {datetime.now().astimezone().strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")

# === Consulta à API da Bitget ===
url = "https://api.bitget.com/api/v2/mix/market/candles"
params = {
    "symbol": "BTCUSDT",
    "productType": "USDT-FUTURES",
    "granularity": "1H",
    "limit": 100
}

try:
    response = requests.get(url, params=params)
    data = response.json()

    if data["code"] == "00000" and data["data"]:
        candles = data["data"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "quote_volume"])
        df = df.astype({"timestamp": "int64", "open": "float", "high": "float", "low": "float", "close": "float"})

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("America/Sao_Paulo")

        # Indicadores
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["std"] = df["close"].rolling(window=20).std()
        df["upper"] = df["ma20"] + 2 * df["std"]
        df["lower"] = df["ma20"] - 2 * df["std"]

        # MACD
        exp1 = df["close"].ewm(span=12, adjust=False).mean()
        exp2 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = exp1 - exp2
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        # RSI
        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        roll_up = pd.Series(gain).rolling(window=14).mean()
        roll_down = pd.Series(loss).rolling(window=14).mean()
        rs = roll_up / roll_down
        df["rsi"] = 100 - (100 / (1 + rs))

        # Último candle
        last = df.iloc[-1]
        previous = df.iloc[-2]
        var_1h = ((last["close"] - previous["close"]) / previous["close"]) * 100
        var_icon = "⬆️" if var_1h > 0.3 else "⬇️" if var_1h < -0.3 else "➖"
        macd_trend = "📉 Baixa" if last["macd"] < last["signal"] else "📈 Alta" if last["macd"] > last["signal"] else "➖ Neutro"
        rsi_trend = "🟢 Sobrecomprado" if last["rsi"] > 70 else "🔴 Sobrevendido" if last["rsi"] < 30 else "🟡 Neutro"

        # === CARD DE RESUMO ===
        st.markdown("""
        ### 🔍 Visão Técnica - BTC/USDT (1H)
        | 💵 Preço Atual | 📊 Variação 1H | 🔼 Limite Sup | 🔽 Limite Inf | 📉 MACD | 📈 RSI |
        |----------------|----------------|----------------|----------------|--------|--------|
        | ${:.2f}         | {:.2f}% {}       | {:.2f}         | {:.2f}         | {}    | {}    |
        """.format(
            last["close"], var_1h, var_icon, last["upper"], last["lower"], macd_trend, rsi_trend
        ))

        # === GRÁFICO ===
        fig = go.Figure()
        df_filtered = df.iloc[-48:]

        fig.add_trace(go.Candlestick(
            x=df_filtered["timestamp"],
            open=df_filtered["open"],
            high=df_filtered["high"],
            low=df_filtered["low"],
            close=df_filtered["close"],
            name="Candles",
            hovertemplate="<b>%{x|%d/%m %Hh}</b><br>🔼 Máx: %{y}<br>🔽 Mín: %{y}<br>"
        ))

        fig.add_trace(go.Scatter(x=df_filtered["timestamp"], y=df_filtered["upper"], mode="lines
