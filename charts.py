import plotly.graph_objects as go
import streamlit as st

def render_price_chart(df, title="📉 BTC/USDT - Últimas 48 horas"):
    df_48h = df[-48:]  # últimas 48 horas

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df_48h["timestamp"],
        open=df_48h["open"],
        high=df_48h["high"],
        low=df_48h["low"],
        close=df_48h["close"],
        name="Candlestick"
    ))

    fig.add_trace(go.Scatter(
        x=df_48h["timestamp"],
        y=df_48h["upper"],
        mode="lines",
        name="BB Superior"
    ))

    fig.add_trace(go.Scatter(
        x=df_48h["timestamp"],
        y=df_48h["ma20"],
        mode="lines",
        name="BB Média"
    ))

    fig.add_trace(go.Scatter(
        x=df_48h["timestamp"],
        y=df_48h["lower"],
        mode="lines",
        name="BB Inferior"
    ))

    fig.update_layout(
        title=f"<b>{title}</b>",
        xaxis_title="Horário",
        yaxis_title="Preço",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
def render_price_section(container, last_price, var_pct, var_icon, var_class):
    """Mostra o preço atual com delta estilizado."""
    with container:
        st.markdown(
            "<div class='titulo-secao'>💲 Preço Atual</div>",
            unsafe_allow_html=True
        )
        st.metric(
            label="Preço (USDT)",
            value=f"{last_price:,.2f}",
            delta=f"{var_icon} {var_pct:.2f}%",
            delta_color="normal"
        )

def render_indicator_table(i1d, i4h, i1h):
    """Monta uma tabela comparativa dos indicadores técnicos."""
    import pandas as pd

    df = pd.DataFrame({
        "Indicador": [
            "Variação %",
            "MACD",
            "RSI",
            "Bandas BB",
            "ADX",
            "SMA Cross",
            "Suporte/Resistência"
        ],
        "1H": i1h,
        "4H": i4h,
        "1D": i1d
    })
    st.markdown(
        "<div class='titulo-secao'>📊 Indicadores Técnicos</div>",
        unsafe_allow_html=True
    )
    st.dataframe(df.set_index("Indicador"), use_container_width=True)

