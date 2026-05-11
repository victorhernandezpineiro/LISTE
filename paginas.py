'''
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def home():
	st.title("Home")

def archivos():
	st.title("Archivos")
	uploaded_file = st.file_uploader("Elige un archivo CSV", type='csv')
	
	# Todo lo relacionado con el archivo debe estar dentro de este 'if'
	# y dentro de la función 'archivos'
	if uploaded_file is not None:
		@st.cache_data  # Corregido: era cache_data, no cache_dataa
		def get_data(file):
			# 1. Lectura del archivo
			df = pd.read_csv(file, encoding="latin1")
			
			# 2. Cálculo de capacidad específica
			if "Capacity(mAh)" in df.columns:
				df["Capacity1(mAh/cm2)"] = df["Capacity(mAh)"] / (np.pi * 0.4**2)
			
			# 3. Identificación de Pasos
			col_mA = "Current(mA)" if "Current(mA)" in df.columns else ("Current(µA)" if "Current(µA)" in df.columns else None)
			
			if col_mA:
				signo = np.sign(df[col_mA])
				cambio = (signo != signo.shift()).fillna(False)
				
				condiciones_base = [df[col_mA] == 0, df[col_mA] > 0, df[col_mA] < 0]
				nombres_base = ["Rest", "Carga", "Descarga"]
				df["_base"] = np.select(condiciones_base, nombres_base, default="Rest")
			
				df["_carga_idx"] = ((df["_base"] == "Carga") & cambio).cumsum()
				df["_descarga_idx"] = ((df["_base"] == "Descarga") & cambio).cumsum()
				
				# Tipo Paso (String)
				df["Tipo Paso"] = np.select(
					[df["_base"] == "Rest", df["_base"] == "Carga", df["_base"] == "Descarga"],
					["Rest", "Carga " + df["_carga_idx"].astype(str), "Descarga " + df["_descarga_idx"].astype(str)],
					default="Rest"
				)
				
				# Paso (Numérico)
				df["Paso"] = np.select(
					[df["_base"] == "Carga", df["_base"] == "Descarga"],
					[df["_carga_idx"], df["_descarga_idx"]],
					default=0
				)
				
				df.drop(columns=["_base", "_carga_idx", "_descarga_idx"], inplace=True)
			
			return df
		datos = get_data(uploaded_file)
		col1, col2 = st.columns(2)
		with col1:
			x_col = st.selectbox("📈 Eje X:", datos.columns.tolist(), index=3)
		with col2:
			opciones_y = [c for c in datos.columns if c != x_col]
			y_default = ["Voltage(V)"] if "Voltage(V)" in opciones_y else []
			y_cols = st.multiselect("📉 Eje Y:", opciones_y, default=y_default)
	
		# Gráfica 1
		if y_cols:
			fig = px.line(datos, x=x_col, y=y_cols, title="Gráfica General")
			st.plotly_chart(fig, use_container_width=True)
	
		# Gráfica 2 (Capacidad específica)
		# Nota: Cambié el nombre a "Capacity1..." para que coincida con tu cálculo de arriba
		if "Capacity1(mAh/cm2)" in datos.columns:
			fig1 = px.line(datos, x="Capacity1(mAh/cm2)", y="Voltage(V)", 
						   color="Paso",line_group="Tipo Paso", title="Capacidad Específica por Paso")
			fig1.update_traces(line=dict(width=3))
			st.plotly_chart(fig1, use_container_width=True)

		#GRafica3
		if "Capacity1(mAh/cm2)" in datos.columns:
		    # 1. Obtener los pasos únicos disponibles en los datos
		    pasos_disponibles = sorted(datos["Paso"].unique())
		
		    # 2. Crear el selector multiopción en la interfaz
		    pasos_seleccionados = st.multiselect(
		        "Selecciona los pasos que deseas representar:",
		        options=pasos_disponibles,
		        default=pasos_disponibles # Por defecto muestra todos
		    )
		
		    # 3. Filtrar los datos según la elección del usuario
		    datos_filtrados = datos[datos["Paso"].isin(pasos_seleccionados)].copy()
		
		    # Convertimos 'Paso' a string para asegurar colores discretos (un color único por paso)
		    datos_filtrados["Paso"] = datos_filtrados["Paso"].astype(str)
		
		    if not datos_filtrados.empty:
		        # 4. Crear el gráfico con los datos filtrados
		        fig1 = px.line(
		            datos_filtrados, 
		            x="Capacity1(mAh/cm2)", 
		            y="Voltage(V)", 
		            color="Paso",           # Esto asigna un color diferente a cada paso
		            line_group="Tipo Paso", 
		            title="Capacidad Específica por Paso (Filtrado)",
		            # Opcional: puedes elegir una paleta específica como px.colors.qualitative.Plotly
		            color_discrete_sequence=px.colors.qualitative.Safe 
		        )
		
		        fig1.update_traces(line=dict(width=3))
		        
		        # 5. Mostrar el gráfico
		        st.plotly_chart(fig1, use_container_width=True)
		    else:
		        st.warning("Selecciona al menos un paso para visualizar el gráfico.")
'''
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io


# =========================================================
# PROCESAMIENTO DE DATOS
# =========================================================
@st.cache_data
def procesar_datos(archivos):

    dfs = []

    for archivo in archivos:

        try:
            # =========================================
            # Lectura segura
            # =========================================
            contenido = archivo.getvalue()

            df = pd.read_csv(
                io.BytesIO(contenido),
                encoding="latin1"
            )

            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()

            # Nombre archivo
            df["Archivo"] = archivo.name

            # =========================================
            # Cálculo capacidad superficial
            # =========================================
            if "Capacity(mAh)" in df.columns:

                area = np.pi * 0.4**2

                df["Capacity1(mAh/cm2)"] = (
                    df["Capacity(mAh)"] / area
                )

            # =========================================
            # Buscar columna de corriente
            # =========================================
            posibles_corrientes = [
                "Current(mA)",
                "Current(µA)",
                "Current(μA)",
                "Current(uA)"
            ]

            col_corriente = next(
                (
                    c for c in posibles_corrientes
                    if c in df.columns
                ),
                None
            )

            # =========================================
            # Crear columnas por defecto
            # =========================================
            df["Paso"] = 0
            df["Tipo Paso"] = "Rest"

            # =========================================
            # Detectar ciclos
            # =========================================
            if col_corriente is not None:

                corriente = pd.to_numeric(
                    df[col_corriente],
                    errors="coerce"
                ).fillna(0)

                # Estado base
                condiciones = [
                    corriente == 0,
                    corriente > 0,
                    corriente < 0
                ]

                nombres = [
                    "Rest",
                    "Carga",
                    "Descarga"
                ]

                df["_base"] = np.select(
                    condiciones,
                    nombres,
                    default="Rest"
                )

                # Detectar inicio REAL
                inicio_carga = (
                    (df["_base"] == "Carga") &
                    (df["_base"].shift() != "Carga")
                )

                inicio_descarga = (
                    (df["_base"] == "Descarga") &
                    (df["_base"].shift() != "Descarga")
                )

                # Contadores
                df["_carga_idx"] = inicio_carga.cumsum()
                df["_descarga_idx"] = inicio_descarga.cumsum()

                # Tipo paso
                df["Tipo Paso"] = np.select(
                    [
                        df["_base"] == "Carga",
                        df["_base"] == "Descarga"
                    ],
                    [
                        "Carga " + df["_carga_idx"].astype(str),
                        "Descarga " + df["_descarga_idx"].astype(str)
                    ],
                    default="Rest"
                )

                # Paso numérico
                df["Paso"] = np.select(
                    [
                        df["_base"] == "Carga",
                        df["_base"] == "Descarga"
                    ],
                    [
                        df["_carga_idx"],
                        df["_descarga_idx"]
                    ],
                    default=0
                ).astype(int)

                # Limpiar temporales
                df.drop(
                    columns=[
                        "_base",
                        "_carga_idx",
                        "_descarga_idx"
                    ],
                    inplace=True
                )

            dfs.append(df)

        except Exception as e:

            st.error(
                f"Error procesando {archivo.name}: {e}"
            )

    # =========================================
    # Validación final
    # =========================================
    if not dfs:
        return pd.DataFrame()

    return pd.concat(
        dfs,
        ignore_index=True
    )


# =========================================================
# INTERFAZ PRINCIPAL
# =========================================================
def comparar():

    st.title("📂 Comparar Capacidades")

    archivos = st.file_uploader(
        "Sube uno o varios archivos CSV:",
        type=["csv"],
        accept_multiple_files=True
    )

    if not archivos:

        st.info(
            "⬆️ Sube uno o varios archivos CSV para comenzar."
        )

        return

    # =====================================================
    # Procesar datos
    # =====================================================
    datos = procesar_datos(archivos)

    if datos.empty:

        st.error("No se pudieron procesar archivos")

        return

    st.success(
        f"✅ {len(archivos)} archivos cargados correctamente."
    )

    # =====================================================
    # Validaciones
    # =====================================================
    columnas_requeridas = [
        "Archivo",
        "Paso",
        "Tipo Paso"
    ]

    faltantes = [
        c for c in columnas_requeridas
        if c not in datos.columns
    ]

    if faltantes:

        st.error(
            f"Faltan columnas: {faltantes}"
        )

        st.write(datos.columns.tolist())

        return

    archivos_disponibles = (
        datos["Archivo"]
        .dropna()
        .unique()
        .tolist()
    )

    # =====================================================
    # GRAFICA GENERAL
    # =====================================================
    st.subheader("📈 Gráfica general")

    columnas_excluidas = [
        "Archivo"
    ]

    columnas = [
        c for c in datos.columns
        if c not in columnas_excluidas
    ]

    if len(columnas) < 2:

        st.warning(
            "No hay suficientes columnas para graficar."
        )

        return

    x_col = st.selectbox(
        "📊 Eje X:",
        columnas,
        index=0
    )

    y_cols = st.multiselect(
        "📉 Eje(s) Y:",
        [c for c in columnas if c != x_col],
        default=[
            c for c in ["Voltage(V)"]
            if c in columnas
        ]
    )

    if y_cols:

        fig = px.line(
            datos,
            x=x_col,
            y=y_cols,
            color="Archivo",
            title="Comparativa general"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # VOLTAJE VS CAPACIDAD
    # =====================================================
    if (
        "Capacity1(mAh/cm2)" not in datos.columns
        or
        "Voltage(V)" not in datos.columns
    ):

        st.warning(
            "No existen columnas necesarias para "
            "Voltaje vs Capacidad."
        )

        return

    st.subheader(
        "⚡ Voltaje vs Capacidad (por ciclo)"
    )

    datos_capacidad = datos.copy()

    # Eliminar Rest
    datos_capacidad = datos_capacidad[
        datos_capacidad["Paso"] > 0
    ]

    if datos_capacidad.empty:

        st.warning(
            "No se detectaron ciclos válidos."
        )

        return

    # =========================================
    # Crear identificador
    # =========================================
    datos_capacidad["Archivo_Ciclo"] = (
        datos_capacidad["Archivo"].astype(str)
        + " - Ciclo "
        + datos_capacidad["Paso"].astype(str)
    )

    # =========================================
    # Rangos automáticos
    # =========================================
    y_min_auto = float(
        datos_capacidad["Voltage(V)"].min()
    )

    y_max_auto = float(
        datos_capacidad["Voltage(V)"].max()
    )

    col1, col2 = st.columns(2)

    with col1:

        valor1 = st.number_input(
            "Valor mínimo eje Y",
            value=y_min_auto,
            format="%.2f"
        )

    with col2:

        valor2 = st.number_input(
            "Valor máximo eje Y",
            value=y_max_auto,
            format="%.2f"
        )

    # =========================================
    # Gráfica
    # =========================================
    fig1 = px.line(
        datos_capacidad,
        x="Capacity1(mAh/cm2)",
        y="Voltage(V)",
        color="Archivo_Ciclo",
        line_group="Tipo Paso",
        title="Voltaje vs Capacidad"
    )

    fig1.update_traces(
        line=dict(width=3)
    )

    fig1.update_yaxes(
        range=[valor1, valor2]
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # =====================================================
    # CICLO ESPECÍFICO
    # =====================================================
    st.subheader(
        "⚡ Voltaje vs Capacidad "
        "(ciclo específico)"
    )

    ciclos = sorted(
        datos_capacidad["Paso"]
        .dropna()
        .unique()
    )

    if len(ciclos) == 0:

        st.warning(
            "No hay ciclos disponibles."
        )

        return

    ciclo_seleccionado = st.selectbox(
        "Selecciona el ciclo:",
        ciclos
    )

    datos_filtrados = datos_capacidad[
        datos_capacidad["Paso"]
        == ciclo_seleccionado
    ].copy()

    fig2 = px.line(
        datos_filtrados,
        x="Capacity1(mAh/cm2)",
        y="Voltage(V)",
        color="Archivo",
        line_group="Tipo Paso",
        title=(
            f"Voltaje vs Capacidad "
            f"- Ciclo {ciclo_seleccionado}"
        )
    )

    fig2.update_traces(
        line=dict(width=3)
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )





































