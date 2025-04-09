
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="BTC/USDT - 1H Técnicos", layout="wide")
st.title("📊 BTC/USDT - Gráfico com Indicadores Técnicos (1H)")

# Última atualização
st.caption(f"⏱️ Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# === Funções para indicadores técnicos ===
def compute_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(period).mean()
    ma_down = down.rolling(period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def compute_bollinger(series, window=20):
    ma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    return ma, upper, lower

# === Requisição à API da Bitget ===
def get_candles_1h(symbol="BTCUSDT", product_type="USDT-FUTURES", granularity=60, limit=200):
    url = "https://api.bitget.com/api/v2/mix/market/candles"
    params = {
        "symbol": symbol,
        "productType": product_type,
        "granularity": granularity,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "00000":
            df = pd.DataFrame(data["data"], columns=[
                "timestamp", "open", "high", "low", "close", "volume", "turnover"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
            df = df.astype({
                "open": float, "high": float, "low": float,
                "close": float, "volume": float
            })
            df = df.sort_values("timestamp").reset_index(drop=True)
            return df
        else:
            st.error(f"Erro da API: {data['msg']}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar à API da Bitget: {e}")
        return None

# === Processamento ===
df = get_candles_1h()
if df is not None:
    df["rsi"] = compute_rsi(df["close"])
    df["macd"], df["macd_signal"] = compute_macd(df["close"])
    df["bb_ma"], df["bb_upper"], df["bb_lower"] = compute_bollinger(df["close"])

    # === Gráfico ===
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candles"
    ))

    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["bb_upper"], name="BB Superior", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["bb_ma"], name="BB Média", line=dict(color="blue", width=1)))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["bb_lower"], name="BB Inferior", line=dict(dash="dot")))

    fig.update_layout(title="BTC/USDT (1H) com Bollinger Bands", xaxis_title="Data", yaxis_title="Preço")

    st.plotly_chart(fig, use_container_width=True)

    # === Subgráficos RSI e MACD ===
    st.subheader("📈 Indicadores Técnicos")

    st.line_chart(df.set_index("timestamp")[["rsi"]].dropna(), height=150, use_container_width=True)
    st.line_chart(df.set_index("timestamp")[["macd", "macd_signal"]].dropna(), height=150, use_container_width=True)

else:
    st.warning("Não foi possível carregar os dados de candles.")
