
import streamlit as st
import requests

st.set_page_config(page_title="Painel BTC/ETH - Futuros Bitget")

st.title("📊 Painel BTC/ETH - Futuros Bitget")

# Verificação de credenciais
with st.expander("🔐 Verificar credenciais carregadas (secrets.toml)"):
    st.code(f"API Key: {st.secrets['bitget']['apiKey']}")
    st.code(f"Secret Key: ✅")
    st.code(f"Passphrase: ✅")

def get_price(symbol, product_type):
    url = f"https://api.bitget.com/api/mix/v1/market/ticker?symbol={symbol}&productType=umcbl"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return float(data['data']['last'])

# Obter preços BTC e ETH com tratamento de erro
st.subheader("📉 Preço Atual (mercado de futuros)")

col1, col2 = st.columns(2)

with col1:
    try:
        btc_price = get_price("BTCUSDT", "umcbl")
        st.success(f"BTC: ${btc_price:,.2f}")
    except Exception as e:
        st.error(f"Erro de conexão (BTCUSDT): {e}")

with col2:
    try:
        eth_price = get_price("ETHUSDT", "umcbl")
        st.success(f"ETH: ${eth_price:,.2f}")
    except Exception as e:
        st.error(f"Erro de conexão (ETHUSDT): {e}")
