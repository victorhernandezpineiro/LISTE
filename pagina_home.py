import streamlit as st
from datetime import datetime

def home(USERS):
    st.title("Home")
    # --- Dentro del bloque de navegación (donde ya estás autenticado) ---
    if st.session_state.get("pagina") == "inicio":
        
        # 1. Encabezado con Logo y Fecha
        col_logo, col_info = st.columns([1, 3])
        
        with col_logo:
            # Sustituye 'logo_grupo.png' por la ruta de tu imagen o una URL
            st.image("liste.png", width=120)
        
        with col_info:
            # Fecha y Hora actual
            ahora = datetime.now().strftime("%d/%m/%Y | %H:%M:%S")
            st.write(f"📅 **Fecha actual:** {ahora}")
            
            # Información del Usuario
            user_name = USERS[st.session_state["username"]]["name"]
            user_role = USERS[st.session_state["username"]]["role"]
            st.markdown(f"👤 **Usuario:** `{user_name}`")
            st.markdown(f"🔑 **Rol:** `{user_role}`")

        st.divider()

        # 2. Título de Bienvenida
        st.title(f"Bienvenido al Portal LISTE, {user_name}")
        st.write("Esta plataforma está diseñada para centralizar el post-procesado de ensayos de caracterización electroquímica.")

        # 3. Descripción de las Secciones (Cards visuales)
        st.subheader("📂 ¿Qué puedes hacer en esta herramienta?")
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("### 📥 Carga de Datos")
            st.write("""
            Importa archivos brutos de tus cicladores Neware. 
            La herramienta detectará las columnas del archivo y calculará la capacidad específica y otros parámetros automáticamente.
            """)
            
        with c2:
            st.success("### 📊 Análisis")
            st.write("""
            Cálculo de capacidades, eficiencias culómbicas y **diferencial de capacidad (dQ/dV)**. 
            Generación de gráficas interactivas.
            """)
            
        with c3:
            st.warning("### 📥 Exportación")
            st.write("""
            Descarga los datos procesados en formato Excel o CSV listos para tus informes o publicaciones.
            """)

        st.divider()

        # 4. Pie de página o aviso de sesión
        st.caption("⚠️ Recuerda: Esta es una sesión temporal. Los datos no guardados se perderán al cerrar el navegador.")

        if st.button("Cerrar Sesión", type="primary"):
            st.session_state["authenticated"] = False
            st.rerun()
