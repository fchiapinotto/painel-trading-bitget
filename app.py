
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BTC/USDT - 1H Candles", layout="wide")
st.title("📊 BTC/USDT - Candles de 1 Hora (Bitget Futuros - v2)")

# Última atualização
st.caption(f"⏱️ Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Requisição à API da Bitget - Versão v2
def get_candles_1h(symbol="BTCUSDT", product_type="USDT-FUTURES", granularity=60, limit=100):
    url = "https://api.bitget.com/api/v2/mix/market/candles"
    params = {
        "symbol": symbol,
        "productType": product_type,
        "granularity": granularity,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["code"] == "00000":
            df = pd.DataFrame(data["data"], columns=[
                "timestamp", "open", "high", "low", "close", "volume", "turnover"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
            df = df.astype({
                "open": float, "high": float, "low": float,
                "close": float, "volume": float
            })
            df = df.sort_values("timestamp").reset_index(drop=True)
            return df
        else:
            st.error(f"Erro da API: {data['msg']}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar à API da Bitget: {e}")
        return None

# Carregar e exibir a tabela
df_candles = get_candles_1h()
if df_candles is not None:
    st.dataframe(df_candles.tail(20), use_container_width=True)
else:
    st.warning("Não foi possível carregar os dados de candles.")
