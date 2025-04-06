
import streamlit as st
import requests
import hmac
import hashlib
import time
import base64
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bitget Futuros BTC/ETH", layout="wide")
st.title("📊 Painel Bitget - Futuros BTC/ETH (USDT-M)")

# === ⚙️ Carregar credenciais do secrets.toml ===
api_key = st.secrets["bitget"]["apiKey"]
secret_key = st.secrets["bitget"]["secretKey"]
passphrase = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"

# === Função para assinar requisições autenticadas ===
def sign_request(timestamp, method, request_path, body_str=""):
    message = f"{timestamp}{method}{request_path}{body_str}"
    mac = hmac.new(secret_key.encode(), message.encode(), digestmod=hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

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

def get_ticker(symbol="BTCUSDT_UMCBL"):
    try:
        url = f"{BASE_URL}/api/mix/v1/market/ticker?symbol={symbol}&productType=umcbl"
        r = requests.get(url, timeout=5)
        return float(r.json()["data"]["last"])
    except Exception as e:
        st.error(f"Erro ao obter preço de {symbol}: {e}")
        return None

def get_position(symbol="BTCUSDT_UMCBL"):
    try:
        endpoint = f"/api/mix/v1/position/single-position?symbol={symbol}&marginCoin=USDT"
        url = BASE_URL + endpoint
        headers = get_auth_headers("GET", endpoint)
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# === Preços ===
btc_price = get_ticker("BTCUSDT_UMCBL")
eth_price = get_ticker("ETHUSDT_UMCBL")

st.subheader("📈 Preços em tempo real (Futuros USDT-M)")
col1, col2 = st.columns(2)
with col1:
    if btc_price:
        st.metric("BTC/USDT", f"${btc_price:,.2f}")
with col2:
    if eth_price:
        st.metric("ETH/USDT", f"${eth_price:,.2f}")

# === Exibir posições abertas ===
st.subheader("📊 Posição Atual (BTC/ETH)")
btc_pos = get_position("BTCUSDT_UMCBL")
eth_pos = get_position("ETHUSDT_UMCBL")
st.write("🔸 BTCUSDT:", btc_pos)
st.write("🔸 ETHUSDT:", eth_pos)

# === Estratégia Sugerida ===
st.subheader("🤖 Estratégia Recomendada")
if btc_price:
    st.markdown(f"**BTC/USDT**\n- Modo: Neutro\n- Faixa sugerida: {btc_price*0.985:,.0f} – {btc_price*1.01:,.0f}\n- Stop: {btc_price*0.97:,.0f}")
if eth_price:
    st.markdown(f"**ETH/USDT**\n- Modo: Neutro\n- Faixa sugerida: {eth_price*0.985:,.0f} – {eth_price*1.01:,.0f}\n- Stop: {eth_price*0.97:,.0f}")

# === 📉 Análise Técnica BTC ===
st.subheader("📉 Análise Técnica BTC/USDT")

def get_candles(symbol="BTCUSDT", interval="1h", limit=200):
    url = f"https://api.bitget.com/api/mix/v1/market/candles?symbol={symbol}&granularity={interval}&limit={limit}&productType=umcbl"
    response = requests.get(url)
    data = response.json()
    if "data" not in data:
        return None
    candles = pd.DataFrame(data["data"], columns=["timestamp","open","high","low","close","volume","turnover"])
    candles["timestamp"] = pd.to_datetime(candles["timestamp"], unit="ms")
    candles.set_index("timestamp", inplace=True)
    candles = candles.astype(float).sort_index()
    return candles

df = get_candles("BTCUSDT", "1h", 200)

if df is not None:
    df["EMA12"] = df["close"].ewm(span=12).mean()
    df["EMA26"] = df["close"].ewm(span=26).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    df["RSI"] = 100 - (100 / (1 + df["close"].diff().apply(lambda x: max(x,0)).rolling(14).mean() / df["close"].diff().apply(lambda x: abs(x)).rolling(14).mean()))
    df["BB_MID"] = df["close"].rolling(20).mean()
    df["BB_UPPER"] = df["BB_MID"] + 2 * df["close"].rolling(20).std()
    df["BB_LOWER"] = df["BB_MID"] - 2 * df["close"].rolling(20).std()

    fig, ax = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
    ax[0].plot(df["close"], label="Close")
    ax[0].plot(df["BB_UPPER"], linestyle="--", label="BB Upper")
    ax[0].plot(df["BB_LOWER"], linestyle="--", label="BB Lower")
    ax[0].set_title("Preço + Bandas de Bollinger")
    ax[0].legend()

    ax[1].plot(df["MACD"], label="MACD", color="blue")
    ax[1].plot(df["Signal"], label="Signal", color="orange")
    ax[1].set_title("MACD")
    ax[1].legend()

    ax[2].plot(df["RSI"], label="RSI", color="purple")
    ax[2].axhline(70, color="red", linestyle="--")
    ax[2].axhline(30, color="green", linestyle="--")
    ax[2].set_title("RSI")
    ax[2].legend()

    ax[3].bar(df.index, df["volume"], label="Volume", color="gray")
    ax[3].set_title("Volume")

    plt.tight_layout()
    st.pyplot(fig)
else:
    st.error("Erro ao obter candles para análise técnica.")
