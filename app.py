import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from datetime import date, timedelta

st.set_page_config(
    page_title="MIA – Sistema de Gestión",
    layout="wide"
)

st.title("🧬 MIA – Sistema de Gestión Regenerativa")

# =========================
# CONEXIÓN A GOOGLE SHEETS
# =========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credenciales = ServiceAccountCredentials.from_json_keyfile_name(
    "credenciales.json", scope
)

cliente = gspread.authorize(credenciales)

sheet = cliente.open_by_url(
    "https://docs.google.com/spreadsheets/d/1QOH3TGu8DHmv0MUha4wlWQMrfI6s4D3fFemDwJiFqjM"
)

# Cargar hojas
ws_pacientes = sheet.worksheet("Pacientes")
ws_tratamientos = sheet.worksheet("Tratamientos")
ws_plus = sheet.worksheet("Plus")
ws_fibro = sheet.worksheet("Fibro Health")

df_pacientes = get_as_dataframe(ws_pacientes).dropna(how="all")
df_tratamientos = get_as_dataframe(ws_tratamientos).dropna(how="all")
df_plus = get_as_dataframe(ws_plus).dropna(how="all")
df_fibro = get_as_dataframe(ws_fibro).dropna(how="all")

# =========================
# FORMULARIO
# =========================

st.subheader("➕ Nuevo tratamiento")

with st.form("form_paciente"):
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre del paciente")

        tratamiento = st.selectbox(
            "Tratamiento",
            df_tratamientos.iloc[:, 0].dropna().unique()
        )

        zonas = st.multiselect(
            "Zona de aplicación",
            [
                "Rostro", "Labios", "Cuello y escote", "Manos",
                "Cuero cabelludo", "Cicatrices y estrías",
                "Rodillas / codos / palmas / plantas",
                "Flacidez"
            ]
        )

    with col2:
        plus = st.multiselect(
            "Plus",
            df_plus.iloc[:, 0].dropna().unique()
        )

        fibro = st.multiselect(
            "Fibro Health",
            df_fibro.iloc[:, 0].dropna().unique()
        )

        intervalo = st.number_input(
            "Intervalo recomendado (días)",
            min_value=1,
            max_value=30,
            value=15
        )

    guardar = st.form_submit_button("💾 Guardar tratamiento")

# =========================
# GUARDADO EN GOOGLE SHEETS
# =========================

if guardar:
    if nombre == "" or not zonas:
        st.warning("⚠️ Completá el nombre del paciente y al menos una zona")
    else:
        fecha_hoy = date.today()
        proximo_turno = fecha_hoy + timedelta(days=intervalo)

        nuevo_registro = pd.DataFrame([{
            "Paciente": nombre,
            "Tratamiento": tratamiento,
            "Zona": ", ".join(zonas),
            "Plus": ", ".join(plus),
            "Fibro Health": ", ".join(fibro),
            "Fecha": str(fecha_hoy),
            "Próximo turno": str(proximo_turno)
        }])

        df_pacientes = pd.concat([df_pacientes, nuevo_registro], ignore_index=True)

        set_with_dataframe(ws_pacientes, df_pacientes)

        st.success("✨ Tratamiento guardado correctamente en la nube")

st.subheader("📋 Pacientes registrados")
st.dataframe(df_pacientes, use_container_width=True)
