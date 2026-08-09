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
GOOGLE_SHEETS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyxJOn5Dy59OpOs23jiSYs6uw8XoKImaKhTPNTrpKl-hp92ZJHEigJ8ynRO4UZQTNq6/exec"

st.title("🌙 NightWash App")
st.subheader("Registro de Inspección y Notificación Nocturna")

st.markdown("---")

# 1. Formulario de Datos del Cliente
st.markdown("### 📋 Datos del Vehículo y Cliente")
cliente_nombre = st.text_input("Nombre del Vecino / Cliente", placeholder="Ej: Carlos Gómez")
placa = st.text_input("Placa del Vehículo", placeholder="Ej: ABC123").upper()

# Campo de teléfono con limpieza automática
telefono_raw = st.text_input("WhatsApp del Cliente (Puedes copiar y pegar desde contactos)", placeholder="Ej: +57 300 123 4567")
telefono_limpio = re.sub(r'\D', '', telefono_raw)

st.markdown("---")

# 2. Captura de Fotos (Soporta JPG, JPEG, PNG y WEBP)
st.markdown("### 📸 Registro Fotográfico (4 Vistas)")
st.caption("📱 *Al tocar cada botón se abrirá la cámara principal de tu celular.*")

# Se agregó "webp" a la lista de formatos permitidos para evitar errores de carga
col1, col2 = st.columns(2)
with col1:
    f_frontal = st.file_uploader("1. Vista Frontal", type=["jpg", "jpeg", "png", "webp"], key="cam1")
    f_trasera = st.file_uploader("2. Vista Trasera", type=["jpg", "jpeg", "png", "webp"], key="cam2")

with col2:
    f_izq = st.file_uploader("3. Lado Izquierdo", type=["jpg", "jpeg", "png", "webp"], key="cam3")
    f_der = st.file_uploader("4. Lado Derecho", type=["jpg", "jpeg", "png", "webp"], key="cam4")

photos = [f_frontal, f_trasera, f_izq, f_der]

st.markdown("---")

# 3. Procesamiento y Generación de Collage
if not cliente_nombre or not placa or not telefono_limpio:
    st.info("👋 Ingresa los datos del cliente y captura las 4 fotos para generar el collage.")
elif not all(photos):
    st.warning("⚠️ Debes capturar las 4 fotos para completar la inspección.")
else:
    # Cargar imágenes capturadas
    imgs = [Image.open(p).convert("RGB") for p in photos]
    w, h = 600, 450
    imgs_resized = [img.resize((w, h)) for img in imgs]
    
    # Crear lienzo de collage
    canvas_w, canvas_h = w * 2, (h * 2) + 120
    collage = Image.new("RGB", (canvas_w, canvas_h), "#0F172A")
    draw = ImageDraw.Draw(collage)
    
    # Identificador de tiempo único
    ahora = datetime.datetime.now()
    fecha_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_filename = ahora.strftime("%Y%m%d_%H%M%S")
    nombre_archivo_unico = f"NightWash_{placa}_{timestamp_filename}.jpg"
    
    # Encabezado
    draw.text((30, 25), "NIGHTWASH - REGISTRO DE INSPECCIÓN EXTERIOR", fill="#38BDF8")
    draw.text((30, 65), f"Vehículo: {placa}  |  Cliente: {cliente_nombre}  |  Fecha: {fecha_str}", fill="#FFFFFF")
    
    # Grilla de fotos
    collage.paste(imgs_resized[0], (0, 120))
    collage.paste(imgs_resized[1], (w, 120))
    collage.paste(imgs_resized[2], (0, 120 + h))
    collage.paste(imgs_resized[3], (w, 120 + h))
    
    # Convertir a bytes
    buf = io.BytesIO()
    collage.save(buf, format="JPEG", quality=90)
    byte_im = buf.getvalue()
    
    st.success("✅ ¡Collage de inspección generado!")
    st.image(byte_im, caption=f"Reporte Visual - Placa: {placa}", use_container_width=True)
    
    # ENVÍO AUTOMÁTICO A GOOGLE SHEETS Y GOOGLE DRIVE
    try:
        imagen_b64 = base64.b64encode(byte_im).decode('utf-8')
        
        payload = {
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "cliente": cliente_nombre,
            "placa": placa,
            "telefono": telefono_limpio,
            "archivo": nombre_archivo_unico,
            "imagen_base64": imagen_b64
        }
        
        res = requests.post(
            GOOGLE_SHEETS_WEBHOOK_URL, 
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if "OK" in res.text or res.status_code == 200:
            st.toast("📊 ¡Servicio y Foto guardados en Drive y Sheets!", icon="✅")
        else:
            st.warning(f"⚠️ Google Sheets respondió con estado: {res.status_code}")
    except Exception as error:
        st.error(f"❌ No se pudo conectar con Google: {error}")

    # 1. BOTÓN DE DESCARGA DIRECTA
    st.download_button(
        label="📥 1. Guardar Collage en Celular",
        data=byte_im,
        file_name=nombre_archivo_unico,
        mime="image/jpeg",
        use_container_width=True
    )
    
    # 2. ENLACE A WHATSAPP
    msg = (
        f"✨ *¡Hola {cliente_nombre}!* ✨\n\n"
        f"🚗 Tu vehículo con placa *{placa}* ya ha sido lavado exteriormente y ha quedado impecable.\n\n"
        f"🌙 *NightWash* cuidó tu carro esta noche para que disfrutes tu día mañana sin perder tiempo.\n\n"
        f"*(Te adjunto en este chat el reporte fotográfico de la inspección)*"
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
                margin-top:10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
                📲 2. Abrir WhatsApp para Enviar Mensaje
            </button>
        </a>
    ''', unsafe_allow_html=True)
