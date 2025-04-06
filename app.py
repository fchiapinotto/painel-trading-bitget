
import streamlit as st
import requests

st.set_page_config(page_title="Painel BTC/ETH - Futuros Bitget", layout="centered")

st.title("📉 Painel BTC/ETH - Futuros Bitget")

with st.expander("🔐 Verificar credenciais carregadas (secrets.toml)"):
    st.code(f"API Key: {st.secrets['bitget']['apiKey']}")
    st.markdown("Secret Key: ✅")
    st.markdown("Passphrase: ✅")

def get_price(symbol: str):
    url = f"https://api.bitget.com/api/mix/v1/market/ticker?symbol={symbol}&productType=umcbl"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data['data']['last'])
    except Exception as e:
        st.error(f"Erro de conexão ({symbol}): {e}")
        return None

st.subheader("📈 Preço Atual (mercado de futuros)")

col1, col2 = st.columns(2)

with col1:
    btc_price = get_price("BTC_USDT")
    if btc_price:
        st.success(f"Preço BTC/USDT: ${btc_price}")
    else:
        st.error("BTC não carregado")

with col2:
    eth_price = get_price("ETH_USDT")
    if eth_price:
        st.success(f"Preço ETH/USDT: ${eth_price}")
    else:
        st.error("ETH não carregado")
