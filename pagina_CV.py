import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def.CV():
    # ============================================================
    # CONFIGURACIÓN
    # ============================================================
    
    st.set_page_config(
        page_title="Análisis de CV",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Análisis de ciclos de CV")
    '''
    
    # ============================================================
    # FUNCIÓN PARA CLASIFICAR LOS CICLOS
    # ============================================================
    
    def clasificar_ciclos(
        df,
        voltage_col="Voltage(V)",
        step_type_col="Step Type",
        rest_value="Rest",
        tolerancia=0.005,
        puntos_necesarios=3
    ):
    
        df = df.copy()
    
        # Crear columna Paso
        df["Paso"] = 0
    
        ciclo = 1
        tendencia_anterior = None
    
        contador_creciente = 0
        contador_decreciente = 0
    
        for i in range(1, len(df)):
    
            # Comprobar que las columnas existen
            if step_type_col in df.columns:
    
                if df.loc[i, step_type_col] == rest_value:
                    df.loc[i, "Paso"] = ciclo
                    continue
    
            # Diferencia de voltaje
            diferencia = (
                df.loc[i, voltage_col]
                - df.loc[i - 1, voltage_col]
            )
    
            # --------------------------------------------
            # Determinar tendencia
            # --------------------------------------------
    
            if diferencia > tolerancia:
    
                contador_creciente += 1
                contador_decreciente = 0
    
            elif diferencia < -tolerancia:
    
                contador_decreciente += 1
                contador_creciente = 0
    
            else:
    
                contador_creciente = 0
                contador_decreciente = 0
    
            # --------------------------------------------
            # Confirmar tendencia
            # --------------------------------------------
    
            tendencia_actual = tendencia_anterior
    
            if contador_creciente >= puntos_necesarios:
    
                tendencia_actual = "creciente"
    
            elif contador_decreciente >= puntos_necesarios:
    
                tendencia_actual = "decreciente"
    
            # --------------------------------------------
            # Detectar nuevo ciclo
            # --------------------------------------------
    
            if (
                tendencia_anterior == "decreciente"
                and tendencia_actual == "creciente"
            ):
                ciclo += 1
    
            # --------------------------------------------
            # Guardar ciclo
            # --------------------------------------------
    
            df.loc[i, "Paso"] = ciclo
    
            tendencia_anterior = tendencia_actual
    
        return df
    
    
    # ============================================================
    # CARGAR ARCHIVOS
    # ============================================================
    
    st.sidebar.header("📂 Archivos")
    
    archivos = st.sidebar.file_uploader(
        "Selecciona uno o varios archivos",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )
    
    
    if not archivos:
    
        st.info("Sube uno o varios archivos CSV o Excel para comenzar.")
    
        st.stop()
    
    
    # ============================================================
    # PARÁMETROS DE CLASIFICACIÓN
    # ============================================================
    
    st.sidebar.header("⚙️ Clasificación")
    
    tolerancia = st.sidebar.number_input(
        "Tolerancia de voltaje (V)",
        min_value=0.0,
        value=0.005,
        step=0.001,
        format="%.4f"
    )
    
    puntos_necesarios = st.sidebar.number_input(
        "Puntos necesarios para confirmar tendencia",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )
    
    
    # ============================================================
    # LEER Y CLASIFICAR ARCHIVOS
    # ============================================================
    
    datasets = {}
    
    for archivo in archivos:
    
        try:
    
            if archivo.name.endswith(".csv"):
    
                df = pd.read_csv(archivo)
    
            else:
    
                df = pd.read_excel(archivo)
    
            # Comprobar Voltage
            if "Voltage(V)" not in df.columns:
    
                st.error(
                    f"❌ {archivo.name}: "
                    "no existe la columna 'Voltage(V)'."
                )
    
                continue
    
            # Clasificar
            df = clasificar_ciclos(
                df,
                voltage_col="Voltage(V)",
                step_type_col="Step Type",
                tolerancia=tolerancia,
                puntos_necesarios=puntos_necesarios
            )
    
            datasets[archivo.name] = df
    
        except Exception as e:
    
            st.error(
                f"❌ Error leyendo {archivo.name}: {e}"
            )
    
    
    if not datasets:
    
        st.stop()
    
    
    # ============================================================
    # SELECCIONAR ARCHIVO
    # ============================================================
    
    st.sidebar.header("📊 Visualización")
    
    archivo_seleccionado = st.sidebar.selectbox(
        "Selecciona el archivo",
        list(datasets.keys())
    )
    
    df = datasets[archivo_seleccionado]
    
    
    # ============================================================
    # INFORMACIÓN DEL DATASET
    # ============================================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Filas",
            len(df)
        )
    
    with col2:
        st.metric(
            "Columnas",
            len(df.columns)
        )
    
    with col3:
        st.metric(
            "Ciclos detectados",
            df["Paso"].max()
        )
    
    
    # ============================================================
    # SELECCIÓN DE CICLOS
    # ============================================================
    
    ciclos = sorted(
        df["Paso"].dropna().unique()
    )
    
    ciclos = [
        int(c)
        for c in ciclos
        if c > 0
    ]
    
    ciclos_seleccionados = st.sidebar.multiselect(
        "Ciclos a representar",
        ciclos,
        default=[ciclos[0]] if ciclos else []
    )
    
    
    # ============================================================
    # SELECCIÓN X / Y
    # ============================================================
    
    columnas_numericas = df.select_dtypes(
        include="number"
    ).columns.tolist()
    
    if "Paso" in columnas_numericas:
        columnas_numericas.remove("Paso")
    
    
    x_col = st.sidebar.selectbox(
        "Eje X",
        columnas_numericas,
        index=(
            columnas_numericas.index("Voltage(V)")
            if "Voltage(V)" in columnas_numericas
            else 0
        )
    )
    
    y_col = st.sidebar.selectbox(
        "Eje Y",
        columnas_numericas,
        index=(
            columnas_numericas.index("Current(A)")
            if "Current(A)" in columnas_numericas
            else 0
        )
    )
    
    
    # ============================================================
    # CREAR GRÁFICO
    # ============================================================
    
    if not ciclos_seleccionados:
    
        st.warning(
            "Selecciona al menos un ciclo."
        )
    
    else:
    
        fig = go.Figure()
    
        for ciclo in ciclos_seleccionados:
    
            datos = df[
                df["Paso"] == ciclo
            ].copy()
    
            fig.add_trace(
                go.Scatter(
                    x=datos[x_col],
                    y=datos[y_col],
                    mode="lines",
                    name=f"Ciclo {ciclo}"
                )
            )
    
        fig.update_layout(
    
            title=(
                f"{archivo_seleccionado} — "
                f"{y_col} vs {x_col}"
            ),
    
            xaxis_title=x_col,
            yaxis_title=y_col,
    
            template="plotly_white",
    
            hovermode="x unified",
    
            height=650
        )
    
        st.plotly_chart(
            fig,
            use_container_width=True
        )
    
    
    # ============================================================
    # MOSTRAR DATOS
    # ============================================================
    
    with st.expander("🔎 Ver datos clasificados"):
    
        st.dataframe(
            df,
            use_container_width=True
        )
    '''
