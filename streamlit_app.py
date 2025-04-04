# fed_liquidity_dashboard/streamlit_app.py

import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Painel de Liquidez do FED", layout="wide")
FRED_API_KEY = "57a975cb3b6c38b1344f6b85ebd760d2"  # Substitua pela sua chave da FRED
FRED_URL = f"https://api.stlouisfed.org/fred/series/observations?series_id=WALCL&api_key={FRED_API_KEY}&file_type=json"

# --- TÍTULO ---
st.title("📊 Painel de Liquidez do FED (WALCL)")

# --- COLETA WALCL ---
walcl_data = requests.get(FRED_URL).json()
dates = [obs["date"] for obs in walcl_data["observations"]]
values = [float(obs["value"]) if obs["value"] != "." else None for obs in walcl_data["observations"]]
df = pd.DataFrame({"Data": pd.to_datetime(dates), "WALCL": values}).dropna()
df.sort_values("Data", inplace=True)
df["Δ Semanal"] = df["WALCL"].diff()

# --- VALORES ATUAIS ---
last_val = df["WALCL"].iloc[-1]
last_val_trilhoes = last_val / 1_000_000
last_delta = df["Δ Semanal"].iloc[-1]
last_delta_bilhoes = last_delta / 1_000

# --- INTERPRETAÇÃO ---
if last_delta > 0:
    interp = f"🟩 Liquidez em expansão (+${last_delta_bilhoes:,.2f} bilhões)"
    insight = "🟢 O Fed está expandindo a liquidez. Potencial suporte ao mercado."
else:
    interp = f"🟥 Liquidez em contração (-${abs(last_delta_bilhoes):,.2f} bilhões)"
    insight = "🔴 O Fed está drenando liquidez. Pode pressionar ações e cripto."

# --- EXIBIÇÃO ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Último valor (WALCL)", f"${last_val_trilhoes:,.2f} Trilhões")
    st.metric("Δ Semanal", f"{last_delta_bilhoes:,.2f} Bilhões")
with col2:
    st.write("**🔍 Interpretação automática:**")
    st.info(interp)
    st.warning(insight)

st.line_chart(df.set_index("Data")["WALCL"])

# --- COMPARATIVO COM ATIVOS ---
import json

# --- Comparativo com Alpha Vantage ---
st.subheader("📈 Comparativo com SP500, Nasdaq e BTC")

AV_API_KEY = "PFB10ASGCSFR1E6W"  # insira sua chave aqui

def get_alpha_series(symbol, market="stock"):
    if market == "crypto":
        url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market=USD&apikey={AV_API_KEY}"
        response = requests.get(url).json()
        data = response.get("Time Series (Digital Currency Daily)", {})
        df = pd.DataFrame({date: float(val["4a. close (USD)"]) for date, val in data.items()}, index=["BTC"]).T
    else:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={AV_API_KEY}"
        response = requests.get(url).json()
        data = response.get("Time Series (Daily)", {})
        df = pd.DataFrame({date: float(val["5. adjusted close"]) for date, val in data.items()}, index=["Price"]).T
    df.index = pd.to_datetime(df.index)
    df.columns = [symbol]
    return df.sort_index()

try:
    spx = get_alpha_series("SPY")
    nasdaq = get_alpha_series("QQQ")
    btc = get_alpha_series("BTC", market="crypto")

    comparativo = pd.concat([spx, nasdaq, btc], axis=1).dropna()
    comparativo = comparativo / comparativo.iloc[0]  # Normalizar

    st.line_chart(comparativo)

except Exception as e:
    st.error(f"❌ Erro ao buscar dados da Alpha Vantage: {e}")

# --- ALERTA AUTOMÁTICO (placeholder) ---
if last_delta_bilhoes < -50:
    st.error("🚨 Alerta: Liquidez caiu mais de $50B. Enviar alerta via n8n/WhatsApp!")

# --- GRÁFICO DE REPO/RRP (em breve) ---
st.subheader("💵 Repos e Reverse Repos (em breve)")
st.caption("Integração em desenvolvimento com dados do New York Fed")
