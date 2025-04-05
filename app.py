
import streamlit as st
import requests
import datetime

# ======= CONFIGURAÇÃO VIA SECRETS =======
api_key = st.secrets["bitget"]["api_key"]
secret_key = st.secrets["bitget"]["secret_key"]
passphrase = st.secrets["bitget"]["passphrase"]

headers = {
    'ACCESS-KEY': api_key,
    'ACCESS-SIGN': '',
    'ACCESS-TIMESTAMP': '',
    'ACCESS-PASSPHRASE': passphrase,
    'Content-Type': 'application/json'
}

# ======= LAYOUT =======
st.set_page_config(page_title="Painel Trading Bitget", layout="wide")
st.title("📊 Painel de Trading - Dados Reais (BTC/ETH)")

# ======= API DE PREÇOS (apenas visual) =======
price_btc = requests.get("https://api.bitget.com/api/spot/v1/market/ticker?symbol=BTCUSDT").json()
price_eth = requests.get("https://api.bitget.com/api/spot/v1/market/ticker?symbol=ETHUSDT").json()

btc_price = float(price_btc['data']['close']) if 'data' in price_btc else "Erro"
eth_price = float(price_eth['data']['close']) if 'data' in price_eth else "Erro"

st.subheader("📈 Preços em Tempo Real")
col1, col2 = st.columns(2)
with col1:
    st.metric("BTC/USDT", f"${btc_price:,.2f}")
with col2:
    st.metric("ETH/USDT", f"${eth_price:,.2f}")

st.markdown("---")

# ======= Estratégia Recomendada com base no preço atual =======
st.subheader("🤖 Estratégia Recomendada")

if isinstance(btc_price, float):
    btc_range_low = btc_price * 0.98
    btc_range_high = btc_price * 1.015
    st.markdown(f"""**BTC/USDT**
- Modo: Long
- Faixa: {btc_range_low:,.0f} – {btc_range_high:,.0f}
- Alavancagem: 3x
- Stop: {btc_range_low * 0.995:,.0f}
""")

if isinstance(eth_price, float):
    eth_range_low = eth_price * 0.985
    eth_range_high = eth_price * 1.02
    st.markdown(f"""**ETH/USDT**
- Modo: Neutro
- Faixa: {eth_range_low:,.0f} – {eth_range_high:,.0f}
- Alavancagem: 2x
- Stop: {eth_range_low * 0.99:,.0f}
""")

st.markdown("---")
st.caption("Última atualização: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M") + " UTC")
