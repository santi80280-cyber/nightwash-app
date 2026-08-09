import streamlit as st
from PIL import Image, ImageDraw
import io
import urllib.parse
import datetime

# Configuración de la página
st.set_page_config(page_title="NightWash App", page_icon="🚗", layout="centered")

st.title("🌙 NightWash App")
st.subheader("Registro de Inspección y Notificación Nocturna")

st.markdown("---")

# 1. Formulario de Datos del Cliente
st.markdown("### 📋 Datos del Vehículo y Cliente")
cliente_nombre = st.text_input("Nombre del Vecino / Cliente", placeholder="Ej: Carlos Gómez")
placa = st.text_input("Placa del Vehículo", placeholder="Ej: ABC123").upper()
telefono = st.text_input("WhatsApp del Cliente (con código de país sin el +)", placeholder="Ej: 573001234567")

st.markdown("---")

# 2. Captura de Fotos con la Cámara del Celular
st.markdown("### 📸 Registro Fotográfico (4 Vistas)")
st.caption("Toma las 4 fotos del exterior del vehículo:")

col1, col2 = st.columns(2)
with col1:
    f_frontal = st.camera_input("1. Vista Frontal")
    f_trasera = st.camera_input("2. Vista Trasera")

with col2:
    f_izq = st.camera_input("3. Lado Izquierdo")
    f_der = st.camera_input("4. Lado Derecho")

photos = [f_frontal, f_trasera, f_izq, f_der]

st.markdown("---")

# 3. Procesamiento y Generación de Collage
if st.button("🚀 Generar Collage y Notificar", type="primary", use_container_width=True):
    if not cliente_nombre or not placa or not telefono:
        st.error("⚠️ Por favor completa el nombre, la placa y el número de WhatsApp.")
    elif not all(photos):
        st.warning("⚠️ Debes tomar las 4 fotos para completar la inspección.")
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
        wa_url = f"https://wa.me/{telefono}?text={encoded_msg}"
        
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
        
        st.info("💡 **Tip de envío:** Al tocar el botón verde, se abrirá WhatsApp con el mensaje redactado. Solo debes presionar el icono de adjuntar imagen y seleccionar el collage que acabas de guardar.")