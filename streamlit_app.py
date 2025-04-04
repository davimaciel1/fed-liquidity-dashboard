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
# --- COMPARATIVO COM ATIVOS USANDO ALPHA VANTAGE ---
st.subheader("📈 Comparativo com SP500, Nasdaq e BTC")

AV_API_KEY = "SUA_CHAVE_ALPHA_VANTAGE"  # Insira sua API Key aqui

def get_stock_series(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={AV_API_KEY}"
    response = requests.get(url).json()
    series = response.get("Time Series (Daily)", {})
    data = {
        pd.to_datetime(date): float(val["5. adjusted close"])
        for date, val in series.items()
        if "5. adjusted close" in val
    }
    return pd.Series(data).sort_index()

def get_crypto_series(symbol):
    url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market=USD&apikey={AV_API_KEY}"
    response = requests.get(url).json()
    series = response.get("Time Series (Digital Currency Daily)", {})
    data = {}
    for date, val in series.items():
        close = val.get("4a. close (USD)")
        if close:
            data[pd.to_datetime(date)] = float(close)
    return pd.Series(data).sort_index()

try:
    spx = get_stock_series("SPY")
    nasdaq = get_stock_series("QQQ")
    btc = get_crypto_series("BTC")

    if spx.empty or nasdaq.empty or btc.empty:
        st.warning("⚠️ Não foi possível obter dados suficientes de SPY, QQQ ou BTC.")
    else:
        comparativo = pd.concat([
            spx.rename("S&P 500"),
            nasdaq.rename("Nasdaq"),
            btc.rename("Bitcoin")
        ], axis=1).dropna()

        if comparativo.empty:
            st.warning("⚠️ As séries não possuem datas em comum suficientes para comparação.")
        else:
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
