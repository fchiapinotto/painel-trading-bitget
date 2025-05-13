import plotly.graph_objects as go
import streamlit as st

def render_candles_bollinger(df, support_resistance=None):
    df_24h = df.tail(24)
    fig = go.Figure()
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df_24h['timestamp'], open=df_24h['open'], high=df_24h['high'],
        low=df_24h['low'], close=df_24h['close'], name='Candles'
    ))
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df_24h['timestamp'], y=df_24h['upper'], mode='lines', name='BB Superior'))
    fig.add_trace(go.Scatter(x=df_24h['timestamp'], y=df_24h['middle'], mode='lines', name='BB Média'))
    fig.add_trace(go.Scatter(x=df_24h['timestamp'], y=df_24h['lower'], mode='lines', name='BB Inferior'))
    # Suportes e Resistências
    if support_resistance:
        sup = support_resistance.get('support')
        res = support_resistance.get('resistance')
        fig.add_hline(y=sup, line_dash='dash', annotation_text='Suporte')
        fig.add_hline(y=res, line_dash='dash', annotation_text='Resistência')
    fig.update_layout(xaxis_title='Hora', yaxis_title='Preço (USDT)', height=400)
    st.plotly_chart(fig, use_container_width=True)
