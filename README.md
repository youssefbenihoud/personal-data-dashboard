# 📊 Personal Data Dashboard

Ein interaktives Dashboard zum Hochladen, Analysieren und Visualisieren von persönlichen Daten (z. B. Finanzen, Aufgaben).  
Ideal für Einsteiger in Data Analysis, Finanztracking oder Streamlit.

---

## 🚀 Funktionen

- 📤 Hochladen von CSV oder Excel-Dateien
- 📊 Automatische Erkennung von Finanzdaten (`amount`, `category`, `date`)
- 📈 Interaktive Diagramme: Kuchendiagramm, Zeitverlauf
- 🔍 Filter nach Kategorie und Zeitraum (via Sidebar)
- 💾 Export als CSV oder Excel
- 🌐 Einfach zu bedienen – keine Programmierkenntnisse nötig

---

## 🛠️ Technologien

- **Streamlit** – Web-Oberfläche
- **Pandas** – Datenanalyse
- **Plotly** – Interaktive Diagramme
- **openpyxl** – Excel-Unterstützung

---

## 🖥️ Lokal starten

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# App starten
streamlit run app.py