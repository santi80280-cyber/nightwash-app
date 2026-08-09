import streamlit as st
from PIL import Image, ImageDraw
import io
import urllib.parse
import datetime
import re

# Configuración de la página
st.set_page_config(page_title="NightWash App", page_icon="🚗", layout="centered")

st.title("🌙 NightWash App")
st.subheader("Registro de Inspección y Notificación Nocturna")

st.markdown("---")

# 1. Formulario de Datos del Cliente
st.markdown("### 📋 Datos del Vehículo y Cliente")
cliente_nombre = st.text_input("Nombre del Vecino / Cliente", placeholder="Ej: Carlos Gómez")
placa = st.text_input("Placa del Vehículo", placeholder="Ej: ABC123").upper()

# Campo de teléfono
telefono_raw = st.text_input("WhatsApp del Cliente (Puedes copiar y pegar desde contactos)", placeholder="Ej: +57 300 123 4567")

# Limpieza del número de teléfono
telefono_limpio = re.sub(r'\D', '', telefono_raw) # Deja solo dígitos

st.markdown("---")

# 2. Captura de Fotos activando la Cámara Nativa del Celular
st.markdown("### 📸 Registro Fotográfico (4 Vistas)")
st.caption("📱 *Al tocar cada botón se abrirá la cámara principal de tu celular.*")

col1, col2 = st.columns(2)
with col1:
    f_frontal = st.file_uploader("1. Vista Frontal", type=["jpg", "jpeg", "png"], key="cam1")
    f_trasera = st.file_uploader("2. Vista Trasera", type=["jpg", "jpeg", "png"], key="cam2")

with col2:
    f_izq = st.file_uploader("3. Lado Izquierdo", type=["jpg", "jpeg", "png"], key="cam3")
    f_der = st.file_uploader("4. Lado Derecho", type=["jpg", "jpeg", "png"], key="cam4")

photos = [f_frontal, f_trasera, f_izq, f_der]

st.markdown("---")

# 3. Procesamiento y Generación de Collage
if st.button("🚀 Generar Collage y Notificar", type="primary", use_container_width=True):
    if not cliente_nombre or not placa or not telefono_limpio:
        st.error("⚠️ Por favor completa el nombre, la placa y el número de WhatsApp.")
    elif not all(photos):
        st.warning("⚠️ Debes tomar o subir las 4 fotos para completar la inspección.")
    else:
        # Cargar imágenes capturadas
        imgs = [Image.open(p).convert("RGB") for p in photos]
        
        # Redimensionar cuadrantes (600x450 px cada uno)
        w, h = 600, 450
        imgs_resized = [img.resize((w, h)) for img in imgs]
        
        # Crear lienzo para el collage (2x2 fotos + encabezado superior)
        canvas_w = w * 2
        canvas_h = (h * 2) + 120
        
        collage = Image.new("RGB", (canvas_w, canvas_h), "#0F172A") # Fondo oscuro profesional
        draw = ImageDraw.Draw(collage)
        
        # Agregar datos al encabezado del collage
        fecha_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        draw.text((30, 25), "NIGHTWASH - REGISTRO DE INSPECCIÓN EXTERIOR", fill="#38BDF8")
        draw.text((30, 65), f"Vehículo: {placa}  |  Cliente: {cliente_nombre}  |  Fecha: {fecha_str}", fill="#FFFFFF")
        
        # Pegar las 4 fotos en la grilla
        collage.paste(imgs_resized[0], (0, 120))
        collage.paste(imgs_resized[1], (w, 120))
        collage.paste(imgs_resized[2], (0, 120 + h))
        collage.paste(imgs_resized[3], (w, 120 + h))
        
        # Convertir collage a bytes para descargar e inspeccionar
        buf = io.BytesIO()
        collage.save(buf, format="JPEG", quality=90)
        byte_im = buf.getvalue()
        
        st.success("✅ ¡Collage generado con éxito!")
        
        # Mostrar vista previa
        st.image(byte_im, caption=f"Reporte Visual - Placa: {placa}", use_container_width=True)
        
        # Botón para guardar la foto en la galería del celular
        st.download_button(
            label="📥 Guardar Collage en Galería",
            data=byte_im,
            file_name=f"NightWash_{placa}_{datetime.date.today()}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
        
        # Crear enlace a WhatsApp con el mensaje predeterminado
        msg = (
            f"✨ *¡Hola {cliente_nombre}!* ✨\n\n"
            f"🚗 Tu vehículo con placa *{placa}* ya ha sido lavado exteriormente y ha quedado impecable.\n\n"
            f"🌙 *NightWash* cuidó tu carro esta noche para que disfrutes tu día mañana sin perder tiempo.\n\n"
            f"*(Te adjunto en este chat el reporte fotográfico de la inspección)*"
        )
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{telefono_limpio}?text={encoded_msg}"
        
        st.markdown("---")
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
        
        st.info("💡 **Tip de envío:** Al tocar el botón verde, se abrirá WhatsApp con el mensaje redactado. Solo presiona el icono de adjuntar imagen y selecciona el collage que acabas de guardar.")
