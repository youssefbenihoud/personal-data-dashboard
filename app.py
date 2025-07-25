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

# Nach dem Laden der CSV
if date_col and date_col in df.columns:
    try:
        df[date_col] = pd.to_datetime(df[date_col])
    except:
        st.warning(f"Spalte '{date_col}' konnte nicht als Datum interpretiert werden.")

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
    # ------------------ Filter (falls Kategorie oder Datum vorhanden) ------------------
    if category_col or date_col:
        st.sidebar.header("🔍 Filter")

        df_filter = df.copy()

        if category_col:
            categories = df[category_col].dropna().unique()
            selected_cats = st.sidebar.multiselect(
                "Kategorie",
                options=categories,
                default=categories
            )
            if selected_cats:
                df_filter = df_filter[df_filter[category_col].isin(selected_cats)]

        if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
            min_date = df[date_col].min().to_pydatetime()
            max_date = df[date_col].max().to_pydatetime()
            start, end = st.sidebar.date_input(
                "Zeitraum",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if start and end:
                mask = (df_filter[date_col] >= pd.Timestamp(start)) & (df_filter[date_col] <= pd.Timestamp(end))
                df_filter = df_filter[mask]

        st.subheader("📋 Gefilterte Daten")
        st.dataframe(df_filter, use_container_width=True)
        df = df_filter  # Weiterverarbeitung mit gefilterten Daten
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

# ------------------ Zeitverlauf (falls Datum erkannt) ------------------
if date_col and amount_col:
    st.subheader("📈 Einnahmen/Ausgaben im Zeitverlauf")
    df_timeline = df[[date_col, amount_col]].copy()
    df_timeline = df_timeline.dropna()
    df_timeline = df_timeline.set_index(date_col).resample("D").sum().reset_index()

    fig2 = px.line(
        df_timeline,
        x=date_col,
        y=amount_col,
        title="Tägliche Transaktionen",
        labels={"amount": "Betrag (€)", "date": "Datum"}
    )
    st.plotly_chart(fig2, use_container_width=True)

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