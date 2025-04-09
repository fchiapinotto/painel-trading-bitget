
import streamlit as st
import requests
import pandas as pd
import hmac
import hashlib
import time
import base64
import plotly.graph_objects as go

# === Configuração da página ===
st.set_page_config(page_title="Bitget BTC/USDT - Técnico", layout="wide")
st.title("📊 Painel Bitget - Futuros BTC/USDT (USDT-M)")

# === Dados de autenticação ===
api_key = st.secrets["bitget"]["apiKey"]
secret_key = st.secrets["bitget"]["secretKey"]
passphrase = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"

# === Assinatura de requisição ===
def sign_request(timestamp, method, request_path, body_str=""):
    message = f"{timestamp}{method}{request_path}{body_str}"
    mac = hmac.new(secret_key.encode(), message.encode(), digestmod=hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

# === Headers com autenticação ===
def get_auth_headers(method, path, body_str=""):
    timestamp = str(int(time.time() * 1000))
    signature = sign_request(timestamp, method, path, body_str)
    return {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json"
    }

# === Função para pegar candles ===
def get_candles(symbol="BTCUSDT_UMCBL", granularity=60, limit=100):
    url = f"{BASE_URL}/api/mix/v1/market/candles?symbol={symbol}&granularity={granularity}&limit={limit}"
    try:
        r = requests.get(url)
        raw = r.json()
        if raw["code"] != "00000":
            return pd.DataFrame()
        df = pd.DataFrame(raw["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "quoteVolume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        df = df.sort_values("timestamp")
        return df
    except Exception as e:
        st.error(f"Erro ao buscar candles: {e}")
        return pd.DataFrame()

# === Obter dados para 1H, 4H, 1D ===
data = {}
periods = {"1H": 60, "4H": 240, "1D": 1440}

for label, g in periods.items():
    df = get_candles("BTCUSDT_UMCBL", granularity=g)
    if not df.empty:
        data[label] = df
    else:
        st.warning(f"Nenhum dado carregado para {label}")

# === Visualização valor atual ===
st.subheader("📈 Preços em tempo real (Futuros USDT-M)")
col1, col2 = st.columns([2, 4])
if "1H" in data and not data["1H"].empty:
    last_price = data["1H"]["close"].iloc[-1]
    col1.metric("BTC/USDT", f"${last_price:,.2f}")
else:
    col1.metric("BTC/USDT", "N/D")

# === Gráfico com plotly ===
if "1H" in data:
    df = data["1H"]
    fig = go.Figure(data=[
        go.Candlestick(x=df["timestamp"],
                       open=df["open"], high=df["high"],
                       low=df["low"], close=df["close"])
    ])
    fig.update_layout(title="Candlestick BTC/USDT (1H)", xaxis_title="Data", yaxis_title="Preço")
    st.plotly_chart(fig, use_container_width=True)
