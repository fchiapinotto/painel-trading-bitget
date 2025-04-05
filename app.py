
import streamlit as st
import requests
import datetime

# Configuração da página
st.set_page_config(page_title="Painel BTC/ETH - Bitget", layout="wide")
st.title("📊 Painel BTC/ETH - Futuros Bitget")

# Função para obter preço de futuros da Bitget
def get_futures_price(symbol, product_type="umcbl"):
    url = f"https://api.bitget.com/api/mix/v1/market/ticker?symbol={symbol}&productType={product_type}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "00000" and "data" in data:
            return float(data["data"].get("last", 0.0))
        else:
            st.error(f"Erro da API para {symbol}: {data.get('msg', 'Resposta inesperada')}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão ({symbol}): {e}")
        return None

# ⚠️ Leitura das credenciais da API (opcional, se configurado)
api_key = st.secrets["bitget"].get("api_key", "NÃO DEFINIDO")
secret_key = st.secrets["bitget"].get("secret_key", "NÃO DEFINIDO")
passphrase = st.secrets["bitget"].get("passphrase", "NÃO DEFINIDO")

with st.expander("🔐 Verificar credenciais carregadas (secrets.toml)"):
    st.code(f"API Key: {api_key}\nSecret Key: {'✔️' if secret_key != 'NÃO DEFINIDO' else '❌'}\nPassphrase: {'✔️' if passphrase != 'NÃO DEFINIDO' else '❌'}")

# Obter os preços atuais
btc_price = get_futures_price("BTCUSDT")
eth_price = get_futures_price("ETHUSDT")

# Exibir os preços
st.subheader("📈 Preço Atual (mercado de futuros)")
col1, col2 = st.columns(2)
with col1:
    if btc_price:
        st.metric("BTC/USDT", f"${btc_price:,.2f}")
    else:
        st.error("BTC não carregado")

with col2:
    if eth_price:
        st.metric("ETH/USDT", f"${eth_price:,.2f}")
    else:
        st.error("ETH não carregado")

# Estratégia sugerida
st.markdown("---")
st.subheader("🤖 Estratégia Recomendada")

if btc_price:
    st.markdown(f"**BTC/USDT**\n- Faixa sugerida: {btc_price*0.985:,.0f} – {btc_price*1.01:,.0f}\n- Modo: Long\n- Stop: {btc_price*0.975:,.0f}")
if eth_price:
    st.markdown(f"**ETH/USDT**\n- Faixa sugerida: {eth_price*0.985:,.0f} – {eth_price*1.01:,.0f}\n- Modo: Neutro\n- Stop: {eth_price*0.975:,.0f}")

# Timestamp da última atualização
st.markdown("---")
st.caption("Última atualização: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S UTC"))
