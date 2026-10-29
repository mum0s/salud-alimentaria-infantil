import io
import textwrap

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Salud Alimentaria Infantil", layout="wide")
st.title("🥗 Salud alimentaria infantil - 4° Grado")

# ---------- ACCESO CON CONTRASEÑA (opcional) ----------
# Si en la nube configurás un secreto llamado "password", la app lo pide.
# En tu computadora, sin secretos configurados, entra directo.
def verificar_acceso():
    try:
        clave = st.secrets["password"]
    except Exception:
        return
    if st.session_state.get("acceso_ok"):
        return
    ingresada = st.text_input("Contraseña", type="password")
    if ingresada and ingresada == clave:
        st.session_state["acceso_ok"] = True
        st.rerun()
    elif ingresada:
        st.error("Contraseña incorrecta")
    st.stop()


verificar_acceso()

# ---------- CARGA DE DATOS ----------
# Si existe data/datos_salud.csv se usa ese archivo; si no (por ejemplo en la
# nube), se pide subir el CSV exportado de Epicollect.
RUTA_CSV = Path(__file__).parent / "data" / "datos_salud.csv"


@st.cache_data
def cargar_datos(contenido):
    return pd.read_csv(io.BytesIO(contenido), encoding="utf-8-sig")


if RUTA_CSV.exists():
    df = cargar_datos(RUTA_CSV.read_bytes())
else:
    archivo = st.file_uploader("Subí el CSV exportado de Epicollect", type="csv")
    if archivo is None:
        st.info("Esperando el archivo CSV para mostrar los gráficos.")
        st.stop()
    df = cargar_datos(archivo.getvalue())

# ---------- RENOMBRAR COLUMNAS ----------
df = df.rename(columns={
    "2_Cuntos_aos_tens":         "edad",
    "3_Especificar_edad":        "edad_texto",
    "4_Con_qu_gnero_te_se":      "genero",
    "5_Tens_alguna_restri":      "restriccion",
    "6_Qu_restriccin_o_co":      "restriccion_detalle",
    "7_Cuntos_das_a_la_se":      "dias_semana_colegio",
    "8_Cunto_tiempo_tens_":      "tiempo_desayuno",
    "9_Quin_prepara_el_de":      "prepara_desayuno",
    "10_Desayuns_solo_o_a":      "desayuno_compania",
    "11_Qu_sols_tomar_ant":      "bebida_desayuno",
    "12_Especificar_bebid":      "bebida_detalle",
    "13_Coms_alguna_fruta":      "come_fruta",
    "14_Con_qu_frecuencia":      "frecuencia_fruta",
    "15_Inclus_cereales_c":      "come_cereales",
    "16_Con_qu_frecuencia":      "frecuencia_cereales",
    "17_Consums_alguno_de":      "snacks",
    "18_Con_qu_frecuencia":      "frecuencia_snacks",
    "19_Almorzs_en_el_com":      "almuerza_colegio",
    "20_Te_gusta_la_comid":      "gusta_comida",
    "21_Sols_terminar_tod":      "termina_comida",
    "22_Al_no_haber_kiosc":      "reaccion_sin_kiosco",
    "23_Qu_elegs_ms_segui":      "eleccion_kiosco",
    "24_Tu_primera_comida":      "primera_comida",
    "25_Hacs_algn_deporte":      "deporte",
})

# ---------- LIMPIEZA ----------
# La edad viene como texto ("10 años"): se extrae solo el número
edad_desde_texto = pd.to_numeric(
    df["edad"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
)
edad_desde_columna = pd.to_numeric(df.get("edad_texto"), errors="coerce")
df["edad"] = edad_desde_texto.fillna(edad_desde_columna)
df = df.dropna(subset=["edad"])

df["grupo_edad"] = pd.cut(
    df["edad"],
    bins=[0, 9, 10, 18],
    labels=["8-9 años", "10 años", "11+ años"]
)

# ---------- MÉTRICAS ----------
tiene_restriccion = (
    df["restriccion"].astype(str).str.strip().str.lower().isin(["si", "sí"])
)

col1, col2,
