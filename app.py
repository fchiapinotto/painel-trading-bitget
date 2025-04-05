
import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Painel de Trading BTC/ETH", layout="wide")
st.title("📊 Painel de Trading - BTC/ETH (Dados Reais)")

# Função para obter o preço atual do contrato futuro perpétuo
def get_price(symbol, product_type):
    url = f"https://api.bitget.com/api/v2/mix/market/ticker?symbol={symbol}&productType={product_type}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['code'] == '00000' and 'data' in data:
            return float(data['data']['lastPr'])
        else:
            st.error(f"Erro na resposta da API para {symbol}: {data.get('msg', 'Resposta inesperada')}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar {symbol}: {e}")
        return None
    except ValueError as e:
        st.error(f"Erro ao processar dados para {symbol}: {e}")
        return None

# Obter preços
btc_price = get_price("BTCUSDT", "USDT-FUTURES")
eth_price = get_price("ETHUSDT", "USDT-FUTURES")

# Exibir preços
st.subheader("📈 Preço Atual (via Bitget API)")
col1, col2 = st.columns(2)
with col1:
    if btc_price is not None:
        st.metric("BTC/USDT", f"${btc_price:,.2f}")
    else:
        st.error("❌ BTC não carregado")

with col2:
    if eth_price is not None:
        st.metric("ETH/USDT", f"${eth_price:,.2f}")
    else:
        st.error("❌ ETH não carregado")

# Estratégia Recomendada
st.markdown("---")
st.subheader("🤖 Estratégia Recomendada (baseada no preço atual)")

if btc_price is not None:
    low = btc_price * 0.985
    high = btc_price * 1.012
    stop = low * 0.995
    st.markdown(f"**BTC/USDT**\n- Modo: Long\n- Faixa: {low:,.0f} – {high:,.0f}\n- Alavancagem: 3x\n- Stop: {stop:,.0f}")

if eth_price is not None:
    low = eth_price * 0.985
    high = eth_price * 1.018
    stop = low * 0.990
    st.markdown(f"**ETH/USDT**\n- Modo: Neutro\n- Faixa: {low:,.0f} – {high:,.0f}\n- Alavancagem: 2x\n- Stop: {stop:,.0f}")

st.markdown("---")
now = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
st.caption("🔄 Última atualização: " + now)
