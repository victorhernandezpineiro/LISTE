import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def procesar_datos(archivos):
    dfs = []
    for archivo in archivos:
        # 1. Lectura del archivo
        df = pd.read_csv(archivo, encoding="latin1")
        df["Archivo"] = archivo.name

        # 2. Cálculos de capacidad
        if "Capacity(mAh)" in df.columns:
            df["Capacity1(mAh/cm2)"] = df["Capacity(mAh)"] / (np.pi * 0.4**2)

        # 3. Identificación de pasos 
        col_mA = "Current(mA)" if "Current(mA)" in df.columns else ("Current(µA)" if "Current(µA)" in df.columns else None)
        
        if col_mA:
            # Detectar cambios de signo para contar ciclos
            signo = np.sign(df[col_mA])
            # True si el signo actual es diferente al anterior
            cambio = (signo != signo.shift()).fillna(False)
            
            # Definir estados base
            condiciones_base = [df[col_mA] == 0, df[col_mA] > 0, df[col_mA] < 0]
            nombres_base = ["Rest", "Carga", "Descarga"]
            df["_base"] = np.select(condiciones_base, nombres_base, default="Rest")

            # Contadores acumulativos por tipo
            df["_carga_idx"] = ((df["_base"] == "Carga") & cambio).cumsum()
            df["_descarga_idx"] = ((df["_base"] == "Descarga") & cambio).cumsum()
            
            # --- CORRECCIÓN DE ERROR DE TIPOS (DType) ---
            # Para "Tipo Paso": Todo debe ser String
            df["Tipo Paso"] = np.select(
                [df["_base"] == "Rest", df["_base"] == "Carga", df["_base"] == "Descarga"],
                [
                    "Rest", 
                    "Carga " + df["_carga_idx"].astype(str), 
                    "Descarga " + df["_descarga_idx"].astype(str)
                ],
                default="Rest"
            )
            
            # Para "Paso": Todo debe ser Int o Float (no mezclar con strings)
            df["Paso"] = np.select(
                [df["_base"] == "Carga", df["_base"] == "Descarga"],
                [df["_carga_idx"], df["_descarga_idx"]],
                default=0
            )
            
            # Limpiar columnas temporales
            df.drop(columns=["_base", "_carga_idx", "_descarga_idx"], inplace=True)

        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)
def comparar():
    st.title("📂 Comparar Capacidades")

    archivos = st.file_uploader(
        "Sube uno o varios archivos CSV:",
        type=["csv"],
        accept_multiple_files=True
    )

    if archivos:
        # Llamada a la función con caché
        datos = procesar_datos(archivos)
        
        archivos_disponibles = datos["Archivo"].unique().tolist()
        st.success(f"✅ {len(archivos)} archivos cargados correctamente.")

        # --- A partir de aquí, el resto de tu código de gráficas permanece idéntico ---
        st.subheader("📈 Gráfica general (comparativa libre)")
        archivos_general = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="general"
        )
        datos_general = datos[datos["Archivo"].isin(archivos_general)]

        columnas = [col for col in datos.columns if col not in ["Archivo", "Tipo Paso"]]
        x_col = st.selectbox("📊 Eje X:", columnas, index=0)
        y_cols = st.multiselect(
            "📉 Eje(s) Y:",
            [col for col in columnas if col != x_col],
            default=["Voltage(V)"]
        )

        if y_cols:
            fig = px.line(
                datos_general,
                x=x_col,
                y=y_cols,
                color="Archivo",
                title=f"Comparativa de {', '.join(y_cols)} vs {x_col}"
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Voltaje vs Capacidad ---
        st.subheader("⚡ Voltaje vs Capacidad (ciclo por archivo)")
        
        archivos_capacidad = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="voltaje"
        )
        
        datos_capacidad = datos[datos["Archivo"].isin(archivos_capacidad)].copy()
        
        # Extraer número de ciclo
        
        # Crear identificador Archivo + Ciclo
        datos_capacidad["Archivo_Ciclo"] = (
            datos_capacidad["Archivo"].astype(str) +
            " - Ciclo " +
            datos_capacidad["Paso"].astype(str)
        )
        
        fig1 = px.line(
            datos_capacidad,
            x="Capacity1(mAh/cm2)",
            y="Voltage(V)",
            color="Archivo_Ciclo",     # mismo color para carga+descarga del ciclo
            line_group="Paso",         # evita que carga y descarga se conecten
            title="Voltaje vs Capacidad - Comparación por ciclo"
        )
        fig1.update_traces(line=dict(width=6))
        fig1.update_layout(
            legend_title="Archivo - Ciclo",
        )
        
        st.plotly_chart(fig1, use_container_width=True)

        #----------------------------------
        st.subheader("⚡ Voltaje vs Capacidad (ciclo específico por archivo)")
        archivos_capacidad = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="voltaje_ciclo"
        )
        
        datos_capacidad = datos[datos["Archivo"].isin(archivos_capacidad)].copy()
        
        # Extraer número de ciclo
        # datos_capacidad["Paso"] = datos_capacidad["Tipo Paso"].str.extract(r'(\d+)')
        
        # Selector de ciclo
        ciclo_seleccionado = st.selectbox(
            "Selecciona el ciclo:",
            sorted(datos_capacidad["Paso"].dropna().unique())
        )
        
        # Filtrar solo el ciclo elegido
        datos_filtrados = datos_capacidad[
            datos_capacidad["Paso"] == ciclo_seleccionado
        ].copy()
        
        # Crear grupo único para evitar que carga y descarga se conecten
        datos_filtrados["Grupo"] = (
            datos_filtrados["Archivo"].astype(str) + "_" +
            datos_filtrados["Tipo Paso"].astype(str)
        )
        
        fig1 = px.line(
            datos_filtrados,
            x="Capacity1(mAh/cm2)",
            y="Voltage(V)",
            color="Archivo",          # 🔥 color fijo por archivo
            line_group="Grupo",       # separa carga y descarga
            title=f"Voltaje vs Capacidad - Ciclo {ciclo_seleccionado}"
        )
        
        fig1.update_traces(line=dict(width=6))
        
        fig1.update_layout(
            legend_title="Archivo",
        )
        
        st.plotly_chart(fig1, use_container_width=True)
       
    else:
        st.info("⬆️ Sube uno o varios archivos CSV para comenzar.")





'''
def comparar():
    st.title("📂 Comparar Capacidades")

    # --- 1️⃣ Subida múltiple ---
    archivos = st.file_uploader(
        "Sube uno o varios archivos CSV:",
        type=["csv"],
        accept_multiple_files=True
    )

    if archivos:
        dfs = []
        for archivo in archivos:
            df = pd.read_csv(archivo,encoding="latin1")

            df["Archivo"] = archivo.name

            # --- 2️⃣ Cálculos adicionales ---
            if "DataPoint" in df.columns:
                df["Time1(h)"] = df["DataPoint"] * 10 / 3600
            if "Capacity(mAh)" in df.columns:
                df["Capacity1(mAh/cm2)"] = df["Capacity(mAh)"] / (np.pi * 0.4**2)
                

            # --- 3️⃣ Identificar pasos de carga/descarga ---
            if "Current(mA)" in df.columns or "Current(µA)" in df.columns:
                current_col = "Current(mA)" if "Current(mA)" in df.columns else "Current(µA)"
                df["Paso"] = ""
                k_carga = 1
                k_descarga = 1
                for i in range(len(df)):
                    current = df.loc[i, current_col]
                    if current == 0:
                        df.loc[i, "Paso"] = "Rest"
                    elif current > 0:
                        df.loc[i, "Paso"] = f"Carga {k_carga}"
                        if i < len(df) - 1 and df.loc[i + 1, current_col] <= 0:
                            k_carga += 1
                    else:
                        df.loc[i, "Paso"] = f"Descarga {k_descarga}"
                        if i < len(df) - 1 and df.loc[i + 1, current_col] >= 0:
                            k_descarga += 1
            dfs.append(df)


        # --- 4️⃣ Unir todos los DataFrames ---
        datos = pd.concat(dfs, ignore_index=True)
        archivos_disponibles = datos["Archivo"].unique().tolist()
        st.success(f"✅ {len(archivos)} archivos cargados correctamente.")

       
        # --- 6️⃣ Gráfica general (X vs Y) ---
        st.subheader("📈 Gráfica general (comparativa libre)")
        archivos_general = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="general"
        )
        datos_general = datos[datos["Archivo"].isin(archivos_general)]

        columnas = [col for col in datos.columns if col not in ["Archivo", "Paso"]]
        x_col = st.selectbox("📊 Eje X:", columnas, index=0)
        y_cols = st.multiselect(
            "📉 Eje(s) Y:",
            [col for col in columnas if col != x_col],
            default=["Voltage(V)"]
        )

        if y_cols:
            fig = px.line(
                datos_general,
                x=x_col,
                y=y_cols,
                color="Archivo",
                title=f"Comparativa de {', '.join(y_cols)} vs {x_col}"
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- 7️⃣ Voltaje vs Capacidad ---
        # --- 7️⃣ Voltaje vs Capacidad ---
        st.subheader("⚡ Voltaje vs Capacidad (ciclo por archivo)")
        
        archivos_capacidad = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="voltaje"
        )
        
        datos_capacidad = datos[datos["Archivo"].isin(archivos_capacidad)].copy()
        
        # Extraer número de ciclo
        datos_capacidad["Ciclo"] = datos_capacidad["Paso"].str.extract(r'(\d+)')
        
        # Crear identificador Archivo + Ciclo
        datos_capacidad["Archivo_Ciclo"] = (
            datos_capacidad["Archivo"].astype(str) +
            " - Ciclo " +
            datos_capacidad["Ciclo"].astype(str)
        )
        
        fig1 = px.line(
            datos_capacidad,
            x="Capacity1(mAh/cm2)",
            y="Voltage(V)",
            color="Archivo_Ciclo",     # mismo color para carga+descarga del ciclo
            line_group="Paso",         # evita que carga y descarga se conecten
            title="Voltaje vs Capacidad - Comparación por ciclo"
        )
        fig1.update_traces(line=dict(width=6))
        fig1.update_layout(
            legend_title="Archivo - Ciclo",
        )
        
        st.plotly_chart(fig1, use_container_width=True)

        #----------------------------------
        st.subheader("⚡ Voltaje vs Capacidad (ciclo específico por archivo)")
        archivos_capacidad = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="voltaje_ciclo"
        )
        
        datos_capacidad = datos[datos["Archivo"].isin(archivos_capacidad)].copy()
        
        # Extraer número de ciclo
        datos_capacidad["Ciclo"] = datos_capacidad["Paso"].str.extract(r'(\d+)')
        
        # Selector de ciclo
        ciclo_seleccionado = st.selectbox(
            "Selecciona el ciclo:",
            sorted(datos_capacidad["Ciclo"].dropna().unique())
        )
        
        # Filtrar solo el ciclo elegido
        datos_filtrados = datos_capacidad[
            datos_capacidad["Ciclo"] == ciclo_seleccionado
        ].copy()
        
        # Crear grupo único para evitar que carga y descarga se conecten
        datos_filtrados["Grupo"] = (
            datos_filtrados["Archivo"].astype(str) + "_" +
            datos_filtrados["Paso"].astype(str)
        )
        
        fig1 = px.line(
            datos_filtrados,
            x="Capacity1(mAh/cm2)",
            y="Voltage(V)",
            color="Archivo",          # 🔥 color fijo por archivo
            line_group="Grupo",       # separa carga y descarga
            title=f"Voltaje vs Capacidad - Ciclo {ciclo_seleccionado}"
        )
        
        fig1.update_traces(line=dict(width=6))
        
        fig1.update_layout(
            legend_title="Archivo",
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
    else:
        st.info("⬆️ Sube uno o varios archivos CSV para comenzar.")
'''
