import pandas as pd

# === Calcula os principais indicadores técnicos para um DataFrame
def compute_indicators(df):
    df["ma20"] = df["close"].rolling(20).mean()
    df["std"] = df["close"].rolling(20).std()
    df["upper"] = df["ma20"] + 2 * df["std"]
    df["lower"] = df["ma20"] - 2 * df["std"]

    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    df["sma50"] = df["close"].rolling(50).mean()
    df["sma200"] = df["close"].rolling(200).mean()
    df["golden_cross"] = df["sma50"] > df["sma200"]

    high, low, close = df["high"], df["low"], df["close"]
    plus_dm = high.diff()
    minus_dm = low.diff()
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df["adx"] = dx.rolling(14).mean()

    return df

# === Gera os ícones e dados resumidos para preenchimento da tabela
def extract_info(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    var = ((last["close"] - prev["close"]) / prev["close"]) * 100

    trend_icon = "🔼" if var > 0 else "🔽" if var < 0 else "➖"
    trend_class = "var-up" if var > 0 else "var-down" if var < 0 else "var-neutral"

    macd_val = last["macd"] - last["signal"]
    macd_icon = "📈" if macd_val > 0 else "📉" if macd_val < 0 else "⏸️"

    rsi_val = last["rsi"]
    rsi_icon = "🟢" if rsi_val > 70 else "🔴" if rsi_val < 30 else "🟡"

    bb_icon = "🟦" if last["close"] > last["upper"] else "🟥" if last["close"] < last["lower"] else "🟨"
    bb_range = f"{last['lower']:,.0f} – {last['upper']:,.0f}"

    adx_icon = "🔥" if last["adx"] > 25 else "💤"
    sma_icon = "💰 Crz. Alta" if last["golden_cross"] else "💀 Crz. Baixa"

    support = df["low"].min()
    resistance = df["high"].max()
    sr_icon = f"🧱 {support:,.0f}<br>🪟 {resistance:,.0f}"

    return (
        f"{trend_icon} <span class='{trend_class}'>{var:.2f}%</span>",
        f"{macd_icon} {macd_val:.2f}",
        f"{rsi_icon} {rsi_val:.1f}",
        f"{bb_icon} {bb_range}",
        f"{adx_icon} {last['adx']:.1f}",
        sma_icon,
        sr_icon
    )
