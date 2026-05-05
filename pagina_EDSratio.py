'''
import streamlit as st
import cv2
import numpy as np
def ratio():
    st.title("Recorte automático de imagen (SEM/EDS)")
    
    # Subir imagen
    uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Leer imagen
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
    
        st.subheader("Imagen original")
        st.image(img, channels="BGR")
    
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
        # Umbral
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    
        # Contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        if contours:
            # Contorno más grande
            largest_contour = max(contours, key=cv2.contourArea)
    
            # Bounding box
            x, y, w, h = cv2.boundingRect(largest_contour)
    
            # Recorte
            cropped = img[y:y+h, x:x+w]
    
            st.subheader("Imagen recortada")
            st.image(cropped, channels="BGR")
    
            # Descargar resultado
            _, buffer = cv2.imencode(".png", cropped)
            st.download_button(
                label="Descargar recorte",
                data=buffer.tobytes(),
                file_name="recorte.png",
                mime="image/png"
            )
        else:
            st.warning("No se encontraron contornos.")
'''

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image
def ratio():
   
    st.title("Visualización de mapas + imagen")
    
    # -----------------------
    # 📂 SUBIDA DE ARCHIVOS
    # -----------------------
    img_file = st.file_uploader("Sube la imagen", type=["png", "jpg", "jpeg"])
    csv_c = st.file_uploader("Sube CSV C", type=["csv"])
    csv_o = st.file_uploader("Sube CSV O", type=["csv"])
    
    # -----------------------
    # 🧠 FUNCIÓN RECORTE
    # -----------------------
    def crop_main_rect(image_np):
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        if len(contours) == 0:
            return image_np
    
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        return image_np[y:y+h, x:x+w]
    
    # -----------------------
    # 📊 CARGA CSV
    # -----------------------
    if csv_c is not None and csv_o is not None:
    
        archivo_C = pd.read_csv(csv_c, header=None)
        archivo_O = pd.read_csv(csv_o, header=None)
    
        # 🔥 RATIO (NO TOCADO EN CONCEPTO, SOLO FORMALIZADO)
        ratio = (archivo_O+1E-10) / (archivo_C+1E-10)  # evita división por cero
    
        st.subheader("Mapa C")
        fig1, ax1 = plt.subplots()
        ax1.imshow(archivo_C.values, cmap="jet")
        st.pyplot(fig1)
    
        st.subheader("Mapa O")
        fig2, ax2 = plt.subplots()
        ax2.imshow(archivo_O.values, cmap="jet")
        st.pyplot(fig2)
    
    # -----------------------
    # 🖼️ PROCESAR IMAGEN
    # -----------------------
    if img_file is not None:
    
        image = Image.open(img_file)
        img_np = np.array(image)
    
        st.subheader("Imagen original")
        st.image(img_np)
    
        use_crop = st.checkbox("¿Quieres recortar automáticamente la imagen?")
    
        if use_crop:
            cropped = crop_main_rect(img_np)
    
            st.subheader("Antes del recorte")
            st.image(img_np)
    
            st.subheader("Después del recorte")
            st.image(cropped)
    
            confirm = st.radio("¿Usar imagen recortada?", ["No", "Sí"])
    
            img_final = cropped if confirm == "Sí" else img_np
        else:
            img_final = img_np
    
    # -----------------------
    # 🔥 SUPERPOSICIÓN FINAL (RATIO)
    # -----------------------
    if img_file is not None and csv_c is not None and csv_o is not None:
    
        st.subheader("Superposición final (Ratio)")
    
        fig3, ax3 = plt.subplots()
    
        ax3.imshow(img_final, cmap='gray')
    
        ax3.imshow(
            ratio.values,
            cmap='jet',
            alpha=0.4,
            extent=[0, img_final.shape[1], img_final.shape[0], 0]
        )
        ax3.colorbar()
    
        ax3.axis("off")
    
        st.pyplot(fig3)
