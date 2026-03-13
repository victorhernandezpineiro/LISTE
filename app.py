import streamlit as st
import paginas as p
import pagina_comparar as p_cp
import pagina_home as p_home
# Diccionario de usuarios
USERS = {
    "victor": {"name": "Victor H.P.", "password": "1234", "role": "Estudiante de doctorado"}#,
    #"maria": {"name": "Maria P.", "password": "abcd", "role": "estudiante TFG"},
    #"leticya": {"name": "Leticya C.M.S", "password": "1021", "role": "Investigador"}
}

# --- Inicializar session_state ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "login"  # página inicial antes del login


# --- Login ---
if not st.session_state.get("authenticated", False):
    st.title("🔒 Login")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if username in USERS and USERS[username]["password"] == password:
            # 1. Actualizamos el estado
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["pagina"] = "inicio"
            
            # 2. Forzamos la recarga inmediata para mostrar la Home
            st.rerun() 
        else:
            st.error("Usuario o contraseña incorrectos")


# --- Contenido de la app después del login ---
if st.session_state["authenticated"]:
    with st.sidebar:
        st.write(f"👤 {USERS[st.session_state['username']]['name']}")
        
        if st.button("🏠 Inicio"):
            st.session_state["pagina"] = "inicio"
        #if st.button("ℹ️ Información"):
           # st.session_state["pagina"] = "informacion"
        if st.button("📂 Visualizar Archivos"):
            st.session_state["pagina"] = "archivos"
        if st.button("📂 Comparar Archivos"):
            st.session_state["pagina"] = "comparar"
        if st.button("🔓 Logout"):
            st.session_state["authenticated"] = False
            st.rerun()
            st.session_state["username"] = ""
            st.session_state["pagina"] = "login"

    # --- Mostrar contenido según página ---
    if st.session_state["pagina"] == "inicio":
        p_home.home(USERS)
    #elif st.session_state["pagina"] == "informacion":
        #st.write("Esta es la página de información")
    elif st.session_state["pagina"] == "archivos":
        p.archivos()
    elif st.session_state["pagina"] == "comparar":
        p_cp.comparar()


















