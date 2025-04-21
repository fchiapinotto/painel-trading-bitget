import pandas as pd
import requests
from indicators import compute_indicators

# === Função de coleta de candles da API Bitget
def fetch_and_process_candles(granularity="1H", limit=100):
    url = "https://api.bitget.com/api/v2/mix/market/candles"
    params = {
        "symbol": "BTCUSDT",
        "productType": "USDT-FUTURES",
        "granularity": granularity,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data["code"] != "00000":
        return None
    df = pd.DataFrame(data["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "quote_volume"])
    df = df.astype({
        "timestamp": "int64",
        "open": "float", "high": "float", "low": "float",
        "close": "float", "volume": "float"
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("America/Sao_Paulo")
    df.sort_values("timestamp", inplace=True)
    return df

# === Função utilitária para carregar os 3 timeframes já com indicadores calculados
def get_all_timeframes():
    df_1h = fetch_and_process_candles("1H")
    df_4h = fetch_and_process_candles("4H")
    df_1d = fetch_and_process_candles("1D")
    if df_1h is not None and df_4h is not None and df_1d is not None:
        return compute_indicators(df_1h), compute_indicators(df_4h), compute_indicators(df_1d)
    return None, None, None
