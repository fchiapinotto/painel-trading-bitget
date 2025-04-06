import streamlit as st
import requests
import hmac
import hashlib
import time
import base64
import json

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

# === 🔹 Obter preço de ticker do contrato futuro ===
def get_ticker(symbol="BTCUSDT_UMCBL"):
    try:
        url = f"{BASE_URL}/api/mix/v1/market/ticker?symbol={symbol}&productType=umcbl"
        r = requests.get(url, timeout=5)
        return float(r.json()["data"]["last"])
    except Exception as e:
        st.error(f"Erro ao obter preço de {symbol}: {e}")
        return None

# === 🔹 Obter posição atual do contrato ===
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
