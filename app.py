# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ------------------ Konfiguration ------------------
st.set_page_config(
    page_title="📊 Personal Data Dashboard",
    layout="wide"
)

# ------------------ Seitenkopf ------------------
st.title("📊 Personal Data Dashboard")
st.markdown("Lade deine Daten hoch und erhalte sofort Einblicke.")

# ------------------ Datei-Upload ------------------
uploaded_file = st.file_uploader(
    "Lade eine CSV-Datei hoch (z. B. transactions.csv)",
    type=["csv", "xlsx"],
    help="Unterstützt CSV und Excel-Dateien"
)

if not uploaded_file:
    st.info("Bitte lade eine Datei hoch, um loszulegen.")
    st.stop()

# ------------------ Daten laden ------------------
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        st.error("Dateiformat nicht unterstützt.")
        st.stop()

    st.success(f"✅ Datei '{uploaded_file.name}' erfolgreich geladen!")
    st.write(f"**Zeilen:** {len(df)} | **Spalten:** {len(df.columns)}")

except Exception as e:
    st.error(f"❌ Fehler beim Lesen der Datei: {e}")
    st.stop()

# ------------------ Daten vorab analysieren ------------------
# Versuche, Finanzdaten zu erkennen
amount_col = next((col for col in df.columns if "amount" in col.lower()), None)
category_col = next((col for col in df.columns if "category" in col.lower()), None)
date_col = next((col for col in df.columns if "date" in col.lower()), None)
desc_col = next((col for col in df.columns if "desc" in col.lower() or "text" in col.lower()), None)

# ------------------ Tabellenansicht ------------------
st.subheader("📋 Datenübersicht")
st.dataframe(df, use_container_width=True)

# ------------------ Statistiken (falls Finanzdaten erkannt) ------------------
if amount_col:
    st.subheader("💰 Finanzstatistiken")

    col1, col2, col3 = st.columns(3)
    total = df[amount_col].sum()
    income = df[df[amount_col] > 0][amount_col].sum()
    expense = df[df[amount_col] < 0][amount_col].sum()

    col1.metric("Gesamtbilanz", f"{total:+.2f} €")
    col2.metric("Einnahmen", f"{income:.2f} €")
    col3.metric("Ausgaben", f"{expense:.2f} €")

    # Diagramm: Ausgaben nach Kategorie
    if category_col:
        st.subheader("📊 Ausgaben nach Kategorie")
        expenses = df[df[amount_col] < 0].copy()
        expenses["Kategorie"] = expenses[category_col].fillna("Unkategorisiert")
        cat_expenses = expenses.groupby("Kategorie")[amount_col].sum().abs()

        fig = px.pie(
            names=cat_expenses.index,
            values=cat_expenses.values,
            title="Ausgabenverteilung"
        )
        st.plotly_chart(fig, use_container_width=True)

# ------------------ Export-Option ------------------
st.subheader("📤 Export")
if st.button("Als CSV exportieren"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="exported_data.csv",
        mime="text/csv"
    )

# Optional: Als Excel
if st.button("Als Excel exportieren"):
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Daten")
    buffer.seek(0)
    st.download_button(
        label="📥 Download Excel",
        data=buffer,
        file_name="exported_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )