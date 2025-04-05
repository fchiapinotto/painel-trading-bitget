
import streamlit as st
import datetime

st.set_page_config(page_title="Painel Trading Bitget", layout="wide")

st.title("📊 Painel de Trading - BTC/ETH")

# Dados simulados até integração com API
st.subheader("📈 Status Atual")
col1, col2 = st.columns(2)
with col1:
    st.metric("BTC/USDT", "$82,150", "-1.2%")
    st.write("RSI (4h): 38.5")
    st.write("MACD (4h): Negativo")
    st.write("Bollinger: banda inferior")
with col2:
    st.metric("ETH/USDT", "$1,818", "-0.9%")
    st.write("RSI (4h): 41.2")
    st.write("MACD (4h): Lateral")
    st.write("Bollinger: testando suporte")

st.markdown("---")

st.subheader("🤖 Estratégia Recomendada")
st.markdown("""
**BTC/USDT**
- Modo: Long
- Faixa: 81.600 – 84.200
- Alavancagem: 3x
- Stop: 80.900

**ETH/USDT**
- Modo: Neutro
- Faixa: 1.825 – 1.915
- Alavancagem: 2x
- Stop: 1.795
""")

st.markdown("---")
st.caption("Última atualização: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M") + " (UTC)")
