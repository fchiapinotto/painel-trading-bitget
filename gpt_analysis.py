import openai
import streamlit as st
from datetime import datetime, timedelta

openai.api_key = st.secrets['openai']['openai_api_key']

@st.cache_data(ttl=24*3600)
def gpt_events():
    prompt = (
        "Liste os eventos relevantes de criptomoedas para hoje e próximos 7 dias..."
    )
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=[{'role':'user','content':prompt}]
    )
    # Espera-se JSON ou lista de objetos com date/title
    return resp.choices[0].message.content  # parse conforme seu formato

@st.cache_data(ttl=900)
def gpt_highlight(df, info):
    prompt = f"Dê um highlight da cotação atual {df['close'].iloc[-1]} e indicadores: {info}"
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=[{'role':'user','content':prompt}], max_tokens=150
    )
    content = resp.choices[0].message.content
    # Separar em sentença e bullets (exemplo simplificado)
    lines = content.split('\n')
    return {'sentenca': lines[0], 'bullets': lines[1:]}

@st.cache_data(ttl=900)
def gpt_grid_scenarios(df, info, events=None):
    prompt = (
        f"Com base em {df['close'].iloc[-1]}, indicadores {info} e eventos {events}, proponha 3 cenários de grid trading: Long, Short, Neutro."
    )
    resp = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=[{'role':'user','content':prompt}], max_tokens=300
    )
    # Espera retorno formatado em JSON
    return resp.choices[0].message.content  # parse conforme o formato desejado
