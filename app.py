import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Painel BTC/USDT", layout="wide")
st.title("📈 Painel Bitget - Futuros BTC/USDT (1H)")
st.caption(f"🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")

# Consulta à API da Bitget
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
        df.sort_values("timestamp", inplace=True)

        # Bollinger
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["std"] = df["close"].rolling(window=20).std()
        df["upper"] = df["ma20"] + 2 * df["std"]
        df["lower"] = df["ma20"] - 2 * df["std"]

        # MACD
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        # RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Últimos valores
        last = df.iloc[-1]
        var_1h = ((last["close"] - df.iloc[-2]["close"]) / df.iloc[-2]["close"]) * 100

        # Ícones
        trend_icon = "🔺" if var_1h > 0 else "🔻" if var_1h < 0 else "⏸️"
        macd_icon = "📈 Alta" if last["macd"] > last["signal"] else "📉 Baixa"
        rsi_icon = "🟢 Sobrecompra" if last["rsi"] > 70 else "🔴 Sobrevenda" if last["rsi"] < 30 else "🟡 Neutro"

        # Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 Último Preço", f"${last['close']:,.2f}")
        col2.metric("📊 Variação 1H", f"{var_1h:.2f}%", trend_icon)
        col3.metric("🔹 Bollinger Sup", f"{last['upper']:,.2f}")
        col4.metric("🔻 Bollinger Inf", f"{last['lower']:,.2f}")
        col5.metric("📉 RSI", f"{last['rsi']:.1f}", rsi_icon)

        # Gráfico
        df_48h = df[-48:]
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df_48h["timestamp"],
            open=df_48h["open"],
            high=df_48h["high"],
            low=df_48h["low"],
            close=df_48h["close"],
            name="Candles"
        ))

        fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["upper"], mode="lines", name="BB Superior",
                                 line=dict(color="blue", dash="dot")))
        fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["ma20"], mode="lines", name="BB Média",
                                 line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["lower"], mode="lines", name="BB Inferior",
                                 line=dict(color="red", dash="dot")))

        fig.update_layout(
            title="📉 BTC/USDT - Últimas 48 horas",
            xaxis_title="Horário",
            yaxis_title="Preço",
            xaxis=dict(tickformat="%d/%m %Hh"),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("❌ Erro ao carregar dados da API Bitget.")

except Exception as e:
    st.error(f"❌ Erro de execução: {e}")
