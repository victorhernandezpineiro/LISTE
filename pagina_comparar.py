import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def comparar():
    st.title("📂 Análisis de Archivos CSV de Baterías")

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
                df["Capacity1(mAh/cm2)"] = df["Capacity(mAh)"] / (np.pi * 4**2)
                

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
        st.subheader("⚡ Voltaje vs Capacidad (ciclo por archivo)")
        
        archivos_capacidad = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="voltaje"
        )
        
        datos_capacidad = datos[datos["Archivo"].isin(archivos_capacidad)].copy()
        
        # Extraer número de ciclo desde la columna Paso
        datos_capacidad["Ciclo"] = datos_capacidad["Paso"].str.extract(r'(\d+)')
        
        # Crear identificador único de ciclo por archivo
        datos_capacidad["Archivo_Ciclo"] = (
            datos_capacidad["Archivo"].astype(str) +
            "_Ciclo_" +
            datos_capacidad["Ciclo"].astype(str)
        )
        
        fig1 = px.line(
            datos_capacidad,
            x="Capacity1(mAh/cm2)",
            y="Voltage(V)",
            color="Archivo",                 # 🔵 cada archivo un color distinto
            line_group="Archivo_Ciclo",      # 🔁 separa ciclos dentro de cada archivo
            line_dash="Paso",                # 🔄 distingue carga/descarga
            title="Voltaje vs Capacidad - Comparación por ciclo"
        )
        
        fig1.update_layout(
            legend_title="Archivo",
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        '''
        # --- 7️⃣ Voltaje vs Capacidad ---
        st.subheader("⚡ Voltaje vs Capacidad (por paso)")
        archivos_capacidad = st.multiselect(
            "Selecciona los archivos para esta gráfica:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="voltaje"
        )
        datos_capacidad = datos[datos["Archivo"].isin(archivos_capacidad)]

        fig1 = px.line(
            datos_capacidad,
            x="Capacity1(mAh/cm2)",
            y="Voltage(V)",
            color="Paso",
            facet_col="Archivo",
            title="Voltaje vs Capacidad diferenciando ciclos y archivos"
        )
        st.plotly_chart(fig1, use_container_width=True)
        '''

    else:
        st.info("⬆️ Sube uno o varios archivos CSV para comenzar.")

