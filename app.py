
import streamlit as st
import requests

st.set_page_config(page_title="Painel de Trading BTC/ETH", layout="wide")

st.title("📊 Painel de Trading - BTC/ETH (Dados Reais)")

def buscar_preco_futuros(symbol):
    url = f"https://api.bitget.com/api/mix/v1/market/ticker?symbol={symbol}&productType=umcbl"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['data']['last'])
    except Exception as e:
        st.error(f"Erro ao buscar {symbol}: {e}")
        return None

# Buscar preços
btc_preco = buscar_preco_futuros("BTCUSDT")
eth_preco = buscar_preco_futuros("ETHUSDT")

st.subheader("📉 Preço Atual (via Bitget API)")
col1, col2 = st.columns(2)

with col1:
    if btc_preco:
        st.metric(label="BTC", value=f"${btc_preco:,.2f}")
    else:
        st.error("❌ BTC não carregado")

with col2:
    if eth_preco:
        st.metric(label="ETH", value=f"${eth_preco:,.2f}")
    else:
        st.error("❌ ETH não carregado")

# Estratégia simulada com base no preço
st.markdown("## 🤖 Estratégia Recomendada (baseada no preço atual)")
if btc_preco and eth_preco:
    if btc_preco < 82000:
        st.warning("📉 BTC abaixo de 82K - possível entrada em **modo SHORT** no grid.")
    elif btc_preco > 86000:
        st.success("📈 BTC acima de 86K - tendência de recuperação, considerar **modo LONG**.")
    else:
        st.info("📊 BTC lateralizado - considerar **modo neutro**.")

    if eth_preco < 1850:
        st.warning("📉 ETH abaixo de 1850 - atenção para suporte. Grid SHORT pode ser vantajoso.")
    elif eth_preco > 1950:
        st.success("📈 ETH acima de 1950 - recuperação em curso. Avaliar grid LONG.")
    else:
        st.info("📊 ETH em consolidação - manter estratégia neutra.")
