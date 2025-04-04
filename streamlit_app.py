import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ---- Configurações da Página ----
st.set_page_config(page_title="Fed Liquidity Tracker", layout="wide")

# ---- Título ----
st.title("📊 Painel de Liquidez do FED (WALCL)")

# ---- Dados da FRED (WALCL) ----
FRED_API_KEY = "57a975cb3b6c38b1344f6b85ebd760d2"
series_id = "WALCL"
url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"

r = requests.get(url)
data = r.json()

dates = [obs["date"] for obs in data["observations"]]
values = [float(obs["value"]) if obs["value"] != "." else None for obs in data["observations"]]

df = pd.DataFrame({"Data": dates, "WALCL": values})
df["Data"] = pd.to_datetime(df["Data"])
df = df.dropna()
df = df.sort_values("Data")

# ---- Variação semanal ----
df["Δ Semanal"] = df["WALCL"].diff()

# ---- Última observação ----
last_val = df["WALCL"].iloc[-1]
last_delta = df["Δ Semanal"].iloc[-1]

# ---- Interpretação ----
if last_delta > 0:
    interp = f"🟩 Liquidez em expansão (+${last_delta:.2f} bilhões)"
else:
    interp = f"🟥 Liquidez em contração (-${abs(last_delta):.2f} bilhões)"

# ---- Layout ----
col1, col2 = st.columns(2)
with col1:
    st.metric("Último valor (WALCL)", f"${last_val:,.2f} B")
    st.metric("Δ Semanal", f"{last_delta:,.2f} B")
with col2:
    st.write("**🔍 Interpretação automática:**")
    st.info(interp)

# ---- Gráfico ----
st.line_chart(df.set_index("Data")[["WALCL"]])
