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

        # --- 5️⃣ Mostrar tabla completa con filtro ---
        st.subheader("📋 Datos de los archivos cargados")
        archivos_tabla = st.multiselect(
            "Selecciona qué archivos mostrar en la tabla:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="tabla"
        )
        datos_tabla = datos[datos["Archivo"].isin(archivos_tabla)]
        st.dataframe(datos_tabla, height=300, use_container_width=True)

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

        # --- 8️⃣ Capacidad final por ciclo (último valor antes de cambio de paso) ---
        st.subheader("🔋 Capacidad final por ciclo (último valor antes de cambio de paso)")

        # Ordenar para asegurar secuencia temporal correcta
        if "Time1(h)" in datos.columns:
            datos_sorted = datos.sort_values(["Archivo", "Time1(h)"])
        elif "DataPoint" in datos.columns:
            datos_sorted = datos.sort_values(["Archivo", "DataPoint"])
        else:
            datos_sorted = datos.reset_index().rename(columns={"index": "_i"}).sort_values(["Archivo", "_i"])

        # Detectar cambios de paso dentro de cada archivo
        datos_sorted["Paso_siguiente"] = datos_sorted.groupby("Archivo")["Paso"].shift(-1)

        # Fila final de cada paso: donde el paso actual != siguiente
        filas_finales = datos_sorted[datos_sorted["Paso"] != datos_sorted["Paso_siguiente"]].copy()

        # Limpiar y renombrar
        columnas_interes = ["Archivo", "Paso"]
        if "Capacity1(mAh/cm2)" in datos_sorted.columns:
            columnas_interes.append("Capacity1(mAh/cm2)")
        if "Voltage(V)" in datos_sorted.columns:
            columnas_interes.append("Voltage(V)")
        if "Time1(h)" in datos_sorted.columns:
            columnas_interes.append("Time1(h)")

        capacidad_final = filas_finales[columnas_interes].rename(
            columns={"Capacity1(mAh/cm2)": "Capacidad final (mAh/cm²)"}
        )

        # Eliminar pasos vacíos o nulos
        capacidad_final = capacidad_final[capacidad_final["Paso"].astype(str).str.strip() != ""]

        # Selección de archivos
        archivos_ciclos = st.multiselect(
            "Selecciona los archivos para la gráfica de capacidad final:",
            archivos_disponibles,
            default=archivos_disponibles,
            key="ciclos"
        )
        capacidad_filtrada = capacidad_final[capacidad_final["Archivo"].isin(archivos_ciclos)]

        # Gráfica y tabla
        fig2 = px.bar(
            capacidad_filtrada,
            x="Paso",
            y="Capacidad final (mAh/cm²)",
            color="Archivo",
            barmode="group",
            title="Capacidad final por ciclo (último valor antes del cambio de paso)"
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(capacidad_filtrada, use_container_width=True)

                # --- 9️⃣ Eficiencia por ciclo ---
        st.subheader("⚙️ Eficiencia de carga/descarga por ciclo")

        # Extraer número de ciclo y tipo de paso
        capacidad_final["Tipo"] = capacidad_final["Paso"].str.extract(r'(Carga|Descarga)', expand=False)
        capacidad_final["Ciclo"] = capacidad_final["Paso"].str.extract(r'(\d+)', expand=False).astype(float)

        # Pivotar para tener una columna para Carga y otra para Descarga
        tabla_pivot = capacidad_final.pivot_table(
            index=["Archivo", "Ciclo"],
            columns="Tipo",
            values="Capacidad final (mAh/cm²)",
            aggfunc="first"
        ).reset_index()

        # Calcular eficiencia (Carga / Descarga)
        tabla_pivot["Eficiencia (Carga/Descarga)"] = tabla_pivot["Carga"] / tabla_pivot["Descarga"] *100

        # Mostrar resultados
        st.dataframe(tabla_pivot, use_container_width=True)

        # --- Gráfica ---
        fig3 = px.bar(
            tabla_pivot,
            x="Ciclo",
            y="Eficiencia (Carga/Descarga)",
            color="Archivo",
            barmode="group",
            title="Eficiencia de carga/descarga por ciclo"
        )
        st.plotly_chart(fig3, use_container_width=True)



    else:
        st.info("⬆️ Sube uno o varios archivos CSV para comenzar.")

