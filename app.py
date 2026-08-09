import streamlit as st
from PIL import Image, ImageDraw
import io
import urllib.parse
import datetime
import re
import requests
import json
import base64

# Configuración de la página
st.set_page_config(page_title="NightWash App", page_icon="🚗", layout="centered")

# 🔗 URL de Google Apps Script
GOOGLE_SHEETS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwFPqY_v-eWyJ7Fyng7bIFvqr4ai3A2BmjZP1uhLSaFYfaq1EzkCR-JjJo8fhGP907eOg/exec"

st.title("🌙 NightWash App")
st.subheader("Registro de Inspección Antes/Después y Notificación Nocturna")

st.markdown("---")

# 1. Formulario de Datos del Cliente
st.markdown("### 📋 Datos del Vehículo y Cliente")
cliente_nombre = st.text_input("Nombre del Vecino / Cliente", placeholder="Ej: Carlos Gómez")
placa = st.text_input("Placa del Vehículo", placeholder="Ej: ABC123").upper()

telefono_raw = st.text_input("WhatsApp del Cliente (Puedes copiar y pegar desde contactos)", placeholder="Ej: +57 300 123 4567")
telefono_limpio = re.sub(r'\D', '', telefono_raw)

st.markdown("---")

# 2. Captura de Fotos ANTES
st.markdown("### 📸 1. Inspección ANTES del Lavado (4 Vistas)")
st.caption("🔴 *Fotos del estado inicial antes de lavar:*")

col1, col2 = st.columns(2)
with col1:
    f_antes_1 = st.file_uploader("1. Antes - Frontal", type=["jpg", "jpeg", "png", "webp"], key="a1")
    f_antes_2 = st.file_uploader("2. Antes - Trasera", type=["jpg", "jpeg", "png", "webp"], key="a2")

with col2:
    f_antes_3 = st.file_uploader("3. Antes - Izquierdo", type=["jpg", "jpeg", "png", "webp"], key="a3")
    f_antes_4 = st.file_uploader("4. Antes - Derecho", type=["jpg", "jpeg", "png", "webp"], key="a4")

photos_antes = [f_antes_1, f_antes_2, f_antes_3, f_antes_4]

st.markdown("---")

# 3. Captura de Fotos DESPUÉS
st.markdown("### 📸 2. Inspección DESPUÉS del Lavado (4 Vistas)")
st.caption("🟢 *Fotos del vehículo completamente limpio:*")

col3, col4 = st.columns(2)
with col3:
    f_despues_1 = st.file_uploader("1. Después - Frontal", type=["jpg", "jpeg", "png", "webp"], key="d1")
    f_despues_2 = st.file_uploader("2. Después - Trasera", type=["jpg", "jpeg", "png", "webp"], key="d2")

with col4:
    f_despues_3 = st.file_uploader("3. Después - Izquierdo", type=["jpg", "jpeg", "png", "webp"], key="d3")
    f_despues_4 = st.file_uploader("4. Después - Derecho", type=["jpg", "jpeg", "png", "webp"], key="d4")

photos_despues = [f_despues_1, f_despues_2, f_despues_3, f_despues_4]

st.markdown("---")

# Función auxiliar para armar collages
def generar_collage(photos, titulo_estado, placa, cliente_nombre, fecha_str):
    imgs = [Image.open(p).convert("RGB") for p in photos]
    w, h = 600, 450
    imgs_resized = [img.resize((w, h)) for img in imgs]
    
    canvas_w, canvas_h = w * 2, (h * 2) + 120
    collage = Image.new("RGB", (canvas_w, canvas_h), "#0F172A")
    draw = ImageDraw.Draw(collage)
    
    draw.text((30, 25), f"NIGHTWASH - INSPECCIÓN {titulo_estado}", fill="#38BDF8")
    draw.text((30, 65), f"Vehículo: {placa}  |  Cliente: {cliente_nombre}  |  Fecha: {fecha_str}", fill="#FFFFFF")
    
    collage.paste(imgs_resized[0], (0, 120))
    collage.paste(imgs_resized[1], (w, 120))
    collage.paste(imgs_resized[2], (0, 120 + h))
    collage.paste(imgs_resized[3], (w, 120 + h))
    
    buf = io.BytesIO()
    collage.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

# Función para enviar a Google al hacer descarga del "Después"
def registrar_en_google_ambos(b_antes, b_despues, file_antes, file_despues, cliente_nombre, placa, telefono_limpio, ahora):
    try:
        b64_antes = base64.b64encode(b_antes).decode('utf-8')
        b64_despues = base64.b64encode(b_despues).decode('utf-8')
        
        payload = {
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "cliente": cliente_nombre,
            "placa": placa,
            "telefono": telefono_limpio,
            "archivo_antes": file_antes,
            "archivo_despues": file_despues,
            "b64_antes": b64_antes,
            "b64_despues": b64_despues
        }
        res = requests.post(
            GOOGLE_SHEETS_WEBHOOK_URL, 
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        if "OK" in res.text or res.status_code == 200:
            st.toast("📊 ¡Registros 'Antes' y 'Después' guardados en Drive y Sheets!", icon="✅")
    except Exception as error:
        st.caption(f"ℹ️ Nota de conexión: {error}")

# Procesamiento principal
if not cliente_nombre or not placa or not telefono_limpio:
    st.info("👋 Ingresa los datos del cliente y completa las fotos para generar los reportes.")
elif not all(photos_antes) or not all(photos_despues):
    st.warning("⚠️ Debes capturar las 4 fotos del ANTES y las 4 fotos del DESPUÉS (8 fotos en total).")
else:
    ahora = datetime.datetime.now()
    fecha_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_filename = ahora.strftime("%Y%m%d_%H%M%S")
    
    file_antes = f"NightWash_ANTES_{placa}_{timestamp_filename}.jpg"
    file_despues = f"NightWash_DESPUES_{placa}_{timestamp_filename}.jpg"
    
    b_antes = generar_collage(photos_antes, "INICIAL (ANTES)", placa, cliente_nombre, fecha_str)
    b_despues = generar_collage(photos_despues, "FINAL (DESPUÉS)", placa, cliente_nombre, fecha_str)
    
    st.success("✅ ¡Collages ANTES y DESPUÉS generados exitosamente!")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("**🔴 Estado Inicial (ANTES)**")
        st.image(b_antes, use_container_width=True)
        # BOTÓN 1: Descargar SOLO el ANTES (sin guardar en Google)
        st.download_button(
            label="📥 Descargar Foto ANTES",
            data=b_antes,
            file_name=file_antes,
            mime="image/jpeg",
            use_container_width=True
        )

    with col_v2:
        st.markdown("**🟢 Estado Final (DESPUÉS)**")
        st.image(b_despues, use_container_width=True)
        # BOTÓN 2: Descargar DESPUÉS Y REGISTRAR EN GOOGLE (Ambas fotos)
        st.download_button(
            label="📥 Descargar Foto DESPUÉS y Registrar en Google",
            data=b_despues,
            file_name=file_despues,
            mime="image/jpeg",
            use_container_width=True,
            on_click=registrar_en_google_ambos,
            args=(b_antes, b_despues, file_antes, file_despues, cliente_nombre, placa, telefono_limpio, ahora)
        )
    
    st.markdown("---")
    
    msg = (
        f"✨ *¡Hola {cliente_nombre}!* ✨\n\n"
        f"🚗 Tu vehículo con placa *{placa}* ha sido lavado exteriormente y ha quedado impecable.\n\n"
        f"🌙 *NightWash* cuidó tu carro esta noche. Te comparto el reporte de cómo quedó terminado."
    )
    encoded_msg = urllib.parse.quote(msg)
    wa_url = f"https://wa.me/{telefono_limpio}?text={encoded_msg}"
    
    st.markdown(f'''
        <a href="{wa_url}" target="_blank">
            <button style="
                background-color:#22C55E; 
                color:white; 
                padding:16px 20px; 
                border:none; 
                border-radius:10px; 
                font-size:16px;
                font-weight:bold; 
                cursor:pointer; 
                width:100%;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
                📲 Abrir WhatsApp para Enviar Mensaje
            </button>
        </a>
    ''', unsafe_allow_html=True)
