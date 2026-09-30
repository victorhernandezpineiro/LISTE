import streamlit as st
import pandas as pd
import plotly.graph_objects as go
'''
def CV():
   import streamlit as st
   import pandas as pd
   import plotly.graph_objects as go
   
   
   # ============================================================
   # CONFIGURACIÓN
   # ============================================================
   
   st.set_page_config(
       page_title="Análisis de CV",
       page_icon="📈",
       layout="wide"
   )
   
   st.title("📈 Análisis de ciclos de CV")
   
   
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
   
       df["Paso"] = 0
   
       ciclo = 1
       tendencia_anterior = None
   
       contador_creciente = 0
       contador_decreciente = 0
   
       for i in range(1, len(df)):
   
           # Si existe la columna Step Type
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
   
   st.header("📂 Cargar archivos")
   
   archivos = st.file_uploader(
       "Selecciona uno o varios archivos CSV o Excel",
       type=["csv", "xlsx"],
       accept_multiple_files=True
   )
   
   
   # ============================================================
   # SI NO HAY ARCHIVOS
   # ============================================================
   
   if not archivos:
   
       st.info(
           "👆 Selecciona uno o varios archivos para comenzar."
       )
   
       st.stop()
   
   
   # ============================================================
   # CONFIGURACIÓN DE CLASIFICACIÓN
   # ============================================================
   
   st.header("⚙️ Configuración de clasificación")
   
   col1, col2 = st.columns(2)
   
   with col1:
   
       tolerancia = st.number_input(
           "Tolerancia de voltaje (V)",
           min_value=0.0,
           value=0.005,
           step=0.001,
           format="%.4f"
       )
   
   with col2:
   
       puntos_necesarios = st.number_input(
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
   
               df = pd.read_csv(archivo,encoding="latin1")
   
           else:
   
               df = pd.read_excel(archivo)
   
           # Comprobar Voltage
           if "Voltage(V)" not in df.columns:
   
               st.error(
                   f"❌ {archivo.name}: "
                   "no existe la columna 'Voltage(V)'."
               )
   
               continue
   
           # Clasificar ciclos
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
   # SELECCIÓN DEL ARCHIVO
   # ============================================================
   
   st.header("📊 Visualización")
   
   archivo_seleccionado = st.selectbox(
       "Selecciona el archivo que quieres analizar",
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
   
   ciclos_seleccionados = st.multiselect(
       "Selecciona los ciclos que quieres representar",
       ciclos,
       default=[ciclos[0]] if ciclos else []
   )
   
   
   # ============================================================
   # SELECCIÓN DE X / Y
   # ============================================================
   
   columnas_numericas = df.select_dtypes(
       include="number"
   ).columns.tolist()
   
   if "Paso" in columnas_numericas:
   
       columnas_numericas.remove("Paso")
   
   
   col1, col2 = st.columns(2)
   
   with col1:
   
       x_col = st.selectbox(
           "Eje X",
           columnas_numericas,
           index=(
               columnas_numericas.index("Voltage(V)")
               if "Voltage(V)" in columnas_numericas
               else 0
           )
       )
   
   
   with col2:
   
       y_col = st.selectbox(
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

def CV():
   import streamlit as st
   import pandas as pd
   import plotly.graph_objects as go
   
   
   # ============================================================
   # CONFIGURACIÓN
   # ============================================================
   
   st.set_page_config(
       page_title="Análisis de CV",
       page_icon="📈",
       layout="wide"
   )
   
   st.title("📈 Análisis de ciclos de CV")
   
   
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
   
           # --------------------------------------------
           # Comprobar Rest
           # --------------------------------------------
   
           if step_type_col in df.columns:
   
               if df.loc[i, step_type_col] == rest_value:
   
                   df.loc[i, "Paso"] = ciclo
                   continue
   
           # --------------------------------------------
           # Diferencia de voltaje
           # --------------------------------------------
   
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
   
   st.header("📂 Cargar archivos")
   
   archivos = st.file_uploader(
       "Selecciona uno o varios archivos CSV o Excel",
       type=["csv", "xlsx"],
       accept_multiple_files=True
   )
   
   
   # ============================================================
   # SI NO HAY ARCHIVOS
   # ============================================================
   
   if not archivos:
   
       st.info(
           "👆 Selecciona uno o varios archivos para comenzar."
       )
   
       st.stop()
   
   
   # ============================================================
   # CONFIGURACIÓN DE CLASIFICACIÓN
   # ============================================================
   
   st.header("⚙️ Configuración de clasificación")
   
   col1, col2 = st.columns(2)
   
   with col1:
   
       tolerancia = st.number_input(
           "Tolerancia de voltaje (V)",
           min_value=0.0,
           value=0.005,
           step=0.001,
           format="%.4f"
       )
   
   with col2:
   
       puntos_necesarios = st.number_input(
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
   
           # --------------------------------------------
           # Leer CSV
           # --------------------------------------------
   
           if archivo.name.lower().endswith(".csv"):
   
               df = pd.read_csv(
                   archivo,
                   encoding="latin1"
               )
   
           # --------------------------------------------
           # Leer Excel
           # --------------------------------------------
   
           else:
   
               df = pd.read_excel(archivo)
   
           # --------------------------------------------
           # Comprobar Voltage(V)
           # --------------------------------------------
   
           if "Voltage(V)" not in df.columns:
   
               st.error(
                   f"❌ {archivo.name}: "
                   "no existe la columna 'Voltage(V)'."
               )
   
               continue
   
           # --------------------------------------------
           # Clasificar ciclos
           # --------------------------------------------
   
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
   
   
   # ============================================================
   # COMPROBAR DATOS
   # ============================================================
   
   if not datasets:
   
       st.error(
           "No se ha podido cargar ningún archivo."
       )
   
       st.stop()
   
   
   # ============================================================
   # VISUALIZACIÓN
   # ============================================================
   
   st.header("📊 Visualización")
   
   
   # ============================================================
   # MODO DE VISUALIZACIÓN
   # ============================================================
   
   modo_visualizacion = st.radio(
       "Modo de visualización",
       [
           "Archivo individual",
           "Comparar varios archivos"
       ],
       horizontal=True
   )
   
   
   # ============================================================
   # SELECCIÓN DE ARCHIVOS
   # ============================================================
   
   if modo_visualizacion == "Archivo individual":
   
       archivo_seleccionado = st.selectbox(
           "Selecciona el archivo",
           list(datasets.keys())
       )
   
       archivos_a_representar = [
           archivo_seleccionado
       ]
   
   else:
   
       archivos_a_representar = st.multiselect(
           "Selecciona los archivos que quieres comparar",
           list(datasets.keys()),
           default=list(datasets.keys())
       )
   
   
   # ============================================================
   # COMPROBAR SELECCIÓN
   # ============================================================
   
   if not archivos_a_representar:
   
       st.warning(
           "Selecciona al menos un archivo."
       )
   
       st.stop()
   
   
   # ============================================================
   # INFORMACIÓN DEL DATASET
   # ============================================================
   
   if modo_visualizacion == "Archivo individual":
   
       df_actual = datasets[
           archivos_a_representar[0]
       ]
   
       col1, col2, col3 = st.columns(3)
   
       with col1:
   
           st.metric(
               "Filas",
               len(df_actual)
           )
   
       with col2:
   
           st.metric(
               "Columnas",
               len(df_actual.columns)
           )
   
       with col3:
   
           st.metric(
               "Ciclos detectados",
               int(df_actual["Paso"].max())
           )
   
   
   # ============================================================
   # CICLOS DISPONIBLES
   # ============================================================
   
   todos_los_ciclos = set()
   
   for archivo in archivos_a_representar:
   
       df_archivo = datasets[archivo]
   
       ciclos_archivo = (
           df_archivo["Paso"]
           .dropna()
           .unique()
       )
   
       for ciclo in ciclos_archivo:
   
           if ciclo > 0:
   
               todos_los_ciclos.add(
                   int(ciclo)
               )
   
   
   todos_los_ciclos = sorted(
       todos_los_ciclos
   )
   
   
   # ============================================================
   # SELECCIÓN DE CICLOS
   # ============================================================
   
   ciclos_seleccionados = st.multiselect(
       "Selecciona los ciclos que quieres representar",
       todos_los_ciclos,
       default=(
           [1]
           if 1 in todos_los_ciclos
           else []
       )
   )
   
   
   # ============================================================
   # COLUMNAS NUMÉRICAS
   # ============================================================
   
   df_referencia = datasets[
       archivos_a_representar[0]
   ]
   
   columnas_numericas = (
       df_referencia
       .select_dtypes(include="number")
       .columns
       .tolist()
   )
   
   
   # No mostrar Paso como eje
   if "Paso" in columnas_numericas:
   
       columnas_numericas.remove("Paso")
   
   
   # ============================================================
   # SELECCIÓN DE X / Y
   # ============================================================
   
   col1, col2 = st.columns(2)
   
   with col1:
   
       x_col = st.selectbox(
           "Eje X",
           columnas_numericas,
           index=(
               columnas_numericas.index("Voltage(V)")
               if "Voltage(V)" in columnas_numericas
               else 0
           )
       )
   
   
   with col2:
   
       y_col = st.selectbox(
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
   
       for archivo in archivos_a_representar:
   
           df_archivo = datasets[archivo]
   
           for ciclo in ciclos_seleccionados:
   
               datos = df_archivo[
                   df_archivo["Paso"] == ciclo
               ].copy()
   
               if datos.empty:
                   continue
   
               # ----------------------------------------
               # Nombre de la curva
               # ----------------------------------------
   
               if modo_visualizacion == "Archivo individual":
   
                   nombre_curva = f"Ciclo {ciclo}"
   
               else:
   
                   nombre_curva = (
                       f"{archivo} - Ciclo {ciclo}"
                   )
   
               # ----------------------------------------
               # Añadir curva
               # ----------------------------------------
   
               fig.add_trace(
                   go.Scatter(
                       x=datos[x_col],
                       y=datos[y_col],
                       mode="lines",
                       name=nombre_curva
                   )
               )
   
   
       # ========================================================
       # CONFIGURACIÓN DEL GRÁFICO
       # ========================================================
   
       fig.update_layout(
   
           title=f"{y_col} vs {x_col}",
   
           xaxis_title=x_col,
   
           yaxis_title=y_col,
   
           template="plotly_white",
   
           hovermode="x unified",
   
           height=650,
   
           legend=dict(
               title="Datos"
           )
       )
   
       st.plotly_chart(
           fig,
           use_container_width=True
       )
   
   
   # ============================================================
   # DATOS CLASIFICADOS
   # ============================================================
   
   with st.expander("🔎 Ver datos clasificados"):
   
       if modo_visualizacion == "Archivo individual":
   
           st.dataframe(
               datasets[
                   archivos_a_representar[0]
               ],
               use_container_width=True
           )
   
       else:
   
           archivo_tabla = st.selectbox(
               "Selecciona el archivo que quieres consultar",
               archivos_a_representar,
               key="archivo_tabla"
           )
   
           st.dataframe(
               datasets[archivo_tabla],
               use_container_width=True
           )

   # ============================================================
# TABLA RESUMEN DE INTENSIDADES
# ============================================================

st.header("📋 Resumen de intensidades")

if not ciclos_seleccionados:

    st.warning(
        "Selecciona al menos un ciclo para generar el resumen."
    )

else:

    resultados = []

    for archivo in archivos_a_representar:

        df_archivo = datasets[archivo]

        # ----------------------------------------------------
        # Filtrar los ciclos seleccionados
        # ----------------------------------------------------

        datos = df_archivo[
            df_archivo["Paso"].isin(ciclos_seleccionados)
        ].copy()

        if datos.empty:
            continue

        # ----------------------------------------------------
        # Comprobar que existen las columnas X e Y
        # ----------------------------------------------------

        if x_col not in datos.columns or y_col not in datos.columns:

            st.warning(
                f"⚠️ {archivo}: no se encuentran las columnas "
                f"seleccionadas ({x_col}, {y_col})."
            )

            continue

        # ----------------------------------------------------
        # Eliminar NaN
        # ----------------------------------------------------

        datos = datos.dropna(
            subset=[x_col, y_col]
        )

        if datos.empty:
            continue

        # ----------------------------------------------------
        # MÁXIMO DE INTENSIDAD
        # ----------------------------------------------------

        indice_max = datos[y_col].idxmax()

        intensidad_max = datos.loc[
            indice_max,
            y_col
        ]

        voltaje_max = datos.loc[
            indice_max,
            x_col
        ]

        # ----------------------------------------------------
        # MÍNIMO DE INTENSIDAD
        # ----------------------------------------------------

        indice_min = datos[y_col].idxmin()

        intensidad_min = datos.loc[
            indice_min,
            y_col
        ]

        voltaje_min = datos.loc[
            indice_min,
            x_col
        ]

        # ----------------------------------------------------
        # DIFERENCIA DE VOLTAJES
        # ----------------------------------------------------

        diferencia_voltaje = (
            voltaje_max - voltaje_min
        )

        # ----------------------------------------------------
        # GUARDAR RESULTADOS
        # ----------------------------------------------------

        resultados.append({

            "Fichero": archivo,

            f"{y_col} máxima": intensidad_max,

            f"{x_col} en máxima": voltaje_max,

            f"{y_col} mínima": intensidad_min,

            f"{x_col} en mínima": voltaje_min,

            "ΔV": diferencia_voltaje

        })

    # ========================================================
    # CREAR TABLA
    # ========================================================

    if resultados:

        df_resumen = pd.DataFrame(
            resultados
        )

        # ----------------------------------------------------
        # Redondear valores numéricos
        # ----------------------------------------------------

        columnas_numericas_resumen = (
            df_resumen
            .select_dtypes(include="number")
            .columns
        )

        df_resumen[
            columnas_numericas_resumen
        ] = df_resumen[
            columnas_numericas_resumen
        ].round(6)

        # ----------------------------------------------------
        # Mostrar tabla
        # ----------------------------------------------------

        st.dataframe(
            df_resumen,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No hay datos disponibles para generar el resumen."
        )
