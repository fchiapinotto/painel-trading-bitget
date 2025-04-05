
import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Painel Trading Bitget", layout="wide")
st.title("📊 Painel de Trading - BTC/ETH (Dados Reais)")

# ===== Atualização de Preço (sem cache) =====
@st.cache_data(ttl=0, show_spinner=False)
def get_price(symbol):
    url = f"https://api.bitget.com/api/spot/v1/market/ticker?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['data']['close'])
    except:
        return None

btc_price = get_price("BTCUSDT")
eth_price = get_price("ETHUSDT")

# ===== Exibição de Cotações =====
st.subheader("📈 Preço Atual (via Bitget API)")
col1, col2 = st.columns(2)
with col1:
    if btc_price:
        st.metric("BTC/USDT", f"${btc_price:,.2f}")
    else:
        st.error("Erro ao obter preço BTC")

with col2:
    if eth_price:
        st.metric("ETH/USDT", f"${eth_price:,.2f}")
    else:
        st.error("Erro ao obter preço ETH")

# ===== Estratégia Recomendada =====
st.markdown("---")
st.subheader("🤖 Estratégia Recomendada (baseada no preço atual)")

if btc_price:
    low = btc_price * 0.985
    high = btc_price * 1.012
    stop = low * 0.995
    st.markdown(f"**BTC/USDT**\n- Modo: Long\n- Faixa: {low:,.0f} – {high:,.0f}\n- Alavancagem: 3x\n- Stop: {stop:,.0f}")

if eth_price:
    low = eth_price * 0.985
    high = eth_price * 1.018
    stop = low * 0.990
    st.markdown(f"**ETH/USDT**\n- Modo: Neutro\n- Faixa: {low:,.0f} – {high:,.0f}\n- Alavancagem: 2x\n- Stop: {stop:,.0f}")

st.markdown("---")
now = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
st.caption("🔄 Última atualização: " + now)
