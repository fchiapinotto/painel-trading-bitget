import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(page_title="Painel BTC/USDT", layout="wide")
st.title("📈 Painel Bitget - Futuros BTC/USDT (1H)")
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
    response = requests.get(url, params=params)
    data = response.json()

    if data["code"] == "00000" and data["data"]:
        candles = data["data"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "quote_volume"])
        df = df.astype({"timestamp": "int64", "open": "float", "high": "float", "low": "float", "close": "float"})

        # Conversão de timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("America/Sao_Paulo")

        # Calcular indicadores
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["std"] = df["close"].rolling(window=20).std()
        df["upper"] = df["ma20"] + 2 * df["std"]
        df["lower"] = df["ma20"] - 2 * df["std"]

        # Gráfico
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Candles"
        ))

        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["upper"], mode="lines", name="BB Superior",
                                 line=dict(color="blue", dash="dot")))
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["ma20"], mode="lines", name="BB Média",
                                 line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["lower"], mode="lines", name="BB Inferior",
                                 line=dict(color="red", dash="dot")))

        fig.update_layout(
            title="BTC/USDT (1H) com Bollinger Bands",
            xaxis_title="Hora",
            yaxis_title="Preço",
            xaxis_rangeslider_visible=False,
            xaxis=dict(
                tickformat="%d/%m %H:00"),
                showgrid=True,
                showline=True
            ),
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Erro ao carregar dados da API Bitget.")

except Exception as e:
    st.error(f"Erro de execução: {e}")
