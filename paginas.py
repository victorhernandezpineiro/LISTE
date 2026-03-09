import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def home():
	st.title("Home")

def archivos():
    st.title("Archivos")
    uploaded_file = st.file_uploader("Elige un archivo CSV", type='csv')

    import pandas as pd
import numpy as np
import streamlit as st

if uploaded_file is not None:
    @st.cache_data
    def get_data(file):
        # 1. Lectura del archivo
        df = pd.read_csv(file, encoding="latin1")
        
        # 2. Cálculo de capacidad específica
        if "Capacity(mAh)" in df.columns:
            # Usamos el nombre de columna del segundo código: Capacity1(mAh/cm2)
            df["Capacity1(mAh/cm2)"] = df["Capacity(mAh)"] / (np.pi * 0.4**2)

        # 3. Identificación de Pasos (Lógica secuencial)
        col_mA = "Current(mA)" if "Current(mA)" in df.columns else ("Current(µA)" if "Current(µA)" in df.columns else None)
        
        if col_mA:
            # Detectar cambios de signo para identificar nuevas etapas
            signo = np.sign(df[col_mA])
            cambio = (signo != signo.shift()).fillna(False)
            
            # Definir estados base
            condiciones_base = [df[col_mA] == 0, df[col_mA] > 0, df[col_mA] < 0]
            nombres_base = ["Rest", "Carga", "Descarga"]
            df["_base"] = np.select(condiciones_base, nombres_base, default="Rest")

            # Contadores acumulativos por tipo (Carga 1, Carga 2...)
            df["_carga_idx"] = ((df["_base"] == "Carga") & cambio).cumsum()
            df["_descarga_idx"] = ((df["_base"] == "Descarga") & cambio).cumsum()
            
            # --- GENERACIÓN DE ETIQUETAS FINALES ---
            
            # Tipo Paso: Columna de texto (String) para leyendas o filtros
            df["Tipo Paso"] = np.select(
                [df["_base"] == "Rest", df["_base"] == "Carga", df["_base"] == "Descarga"],
                [
                    "Rest", 
                    "Carga " + df["_carga_idx"].astype(str), 
                    "Descarga " + df["_descarga_idx"].astype(str)
                ],
                default="Rest"
            )
            
            # Paso: Columna numérica (Integer) para cálculos o ejes X
            df["Paso"] = np.select(
                [df["_base"] == "Carga", df["_base"] == "Descarga"],
                [df["_carga_idx"], df["_descarga_idx"]],
                default=0
            )
            
            # Limpiar columnas auxiliares
            df.drop(columns=["_base", "_carga_idx", "_descarga_idx"], inplace=True)

        return df
  		# Ejecución
   		datos = get_data(uploaded_file)
        
        # --- UI y Gráficos ---
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("📈 Eje X:", datos.columns.tolist(), index=0) # Ajustado index para evitar error si hay pocas columnas
        with col2:
            opciones_y = [c for c in datos.columns if c != x_col]
            y_cols = st.multiselect("📉 Eje Y:", opciones_y, default=["Voltage(V)"] if "Voltage(V)" in opciones_y else [])

        # Gráfica 1
        fig = px.line(datos, x=x_col, y=y_cols, title="Gráfica General")
        st.plotly_chart(fig, use_container_width=True)

        # Gráfica 2 (Capacidad específica)
        if "Specific Capacity(mAh/cm2)" in datos.columns:
            fig1 = px.line(datos, x="Specific Capacity(mAh/cm2)", y="Voltage(V)", 
                           color="Paso", title="Capacidad Específica por Paso")
            fig1.update_traces(line=dict(width=3))
            st.plotly_chart(fig1, use_container_width=True)
'''
def archivos():
	st.title("Archivos")
	uploaded_file = st.file_uploader("Elige un archivo CSV", type='csv')
	# corriente_carga = st.number_input("Introduce la corriente de carga:")
	# corriente_descarga = st.number_input("Introduce la corriente de descarga:")
	if uploaded_file is not None:	
		datos=pd.read_csv(uploaded_file,encoding="latin1")
		st.write("### 📋 Datos")
		#datos["Time1(h)"]=datos["DataPoint"]*10/3600
		for i in range(len(datos)):
			if datos.loc[i, "Step Type"] == "CV Chg": # or datos.loc[i, "Step Type"] == "CCCV Chg":
				paso=0
				#datos.loc[i, "Capacity1(mAh/cm2)"] = datos.loc[i, "Capacity(mAh)"] / (np.pi * 0.4**2) + datos.loc[i - 1, "Capacity1(mAh/cm2)"] Esta liena queda comentada mientras no sepa para que la empleaba. Por ahora parece que no da fallo el codigo
			else:
				datos.loc[i, "Capacity1(mAh/cm2)"] = datos.loc[i, "Capacity(mAh)"] / (np.pi * 0.4**2)

			if datos.loc[i,"Capacity1(mAh/cm2)"]==0:
				datos.loc[i,"Capacity1(mAh/cm2)"]= None


		if "Current(mA)" in datos.columns or "Current(µA)" in datos.columns:
			current_col = "Current(mA)" if "Current(mA)" in datos.columns else "Current(µA)"
			datos["Paso"]=""
			datos["Ciclo"]=0
			print (datos.keys())
			k_carga = 1
			k_descarga = 1
	
			
	
			for i in range(len(datos)):
				if "Current(mA)" in datos.columns:
					current = datos.loc[i, "Current(mA)"]
					columnname = "Current(mA)"
				elif "Current(µA)" in datos.columns:
					current = datos.loc[i, "Current(µA)"]
					columnname = "Current(µA)"
					
				if datos.loc[i,"Step Type"] == "Rest":
					datos.loc[i, "Paso"] = "Rest"
					#datos.loc[i, "Ciclo"] = 0
				elif current >= 0 and (datos.loc[i,"Step Type"] == "CC Chg" or datos.loc[i,"Step Type"] == "CCCV Chg"):
					datos.loc[i, "Paso"] = f"Charge {k_carga}"
					datos.loc[i, "Ciclo"] = k_carga
					# Si el siguiente valor cambia de signo o a cero, pasamos al siguiente ciclo
					if i < len(datos) - 1 and datos.loc[i+1, columnname] <= 0:
						k_carga += 1
				elif current <= 0 and datos.loc[i,"Step Type"] == "CC DChg":
					datos.loc[i, "Paso"] = f"Discharge {k_descarga}"
					datos.loc[i, "Ciclo"] = k_descarga
					if i < len(datos) - 1 and datos.loc[i+1, columnname] >= 0:
						k_descarga += 1
				


		st.dataframe(datos)

		columnas = datos.columns.tolist()

		x_col = st.selectbox("📈 Elige el eje X:", columnas, index=0)
		y_cols = st.multiselect(
			"📉 Elige una o varias variables para el eje Y:",
			options=[col for col in columnas if col != x_col],
			default=["Voltage(V)"]
		)
		# plt.plot(datos["DataPoint"],datos["Voltage(V)"])
		fig=px.line( datos, x_col,y=y_cols)
		# fig=px.line(datos, x="Capacity(Ah)",y="Voltage(V)")
		fig.layout.title="Voltaje vs DataPoint"
		st.plotly_chart(fig, use_container_width=True)

		fig1=px.line( datos, "Capacity1(mAh/cm2)", "Voltage(V)",color="Ciclo")
		st.plotly_chart(fig1, use_container_width=True)


		capacidad_max = []

		for i in range(1, len(datos)):  # empieza en 1 para poder usar i-1
			if datos.loc[i, "Paso"] != datos.loc[i - 1, "Paso"]:
				capacidad_max.append([
					datos.loc[i-1, "DataPoint"],
					datos.loc[i - 1, "Paso"],
					datos.loc[i - 1, "Capacity1(mAh/cm2)"]
				])
			elif i == len(datos) - 1:  # último punto
				capacidad_max.append([
					datos.loc[i, "DataPoint"],
					datos.loc[i, "Paso"],
					datos.loc[i, "Capacity1(mAh/cm2)"]
				])
		df1= pd.DataFrame(capacidad_max, columns=["DataPoint", "Ciclo", "Capacidad máxima (mAh/cm2)"])
		st.dataframe(df1)

		# --- 2️⃣ Calcular eficiencia (Descarga/Carga * 100) ---
		# Extraer el tipo de paso (Carga o Descarga) y número de ciclo
		df1["Tipo"] = df1["Ciclo"].str.extract(r'(Charge|Discharge)', expand=False)
		df1["Nº ciclo"] = df1["Ciclo"].str.extract(r'(\d+)', expand=False).astype(float)

		# Pivotar la tabla para tener columnas separadas
		tabla_ef = df1.pivot_table(
			index="Nº ciclo",
			columns="Tipo",
			values="Capacidad máxima (mAh/cm2)",
			aggfunc="first"
		).reset_index()

		# Calcular la eficiencia
		tabla_ef["Eficiencia (%)"] = (tabla_ef["Charge"] / tabla_ef["Discharge"]) * 100

		st.subheader("⚙️ Eficiencia de descarga/carga por ciclo")
		st.dataframe(tabla_ef, use_container_width=True)

		# # --- 3️⃣ (Opcional) Representar gráficamente ---
		# import plotly.express as px

		# fig = px.bar(
		# 	tabla_ef,
		# 	x="Nº ciclo",
		# 	y="Eficiencia (%)",
		# 	title="Eficiencia de descarga/carga por ciclo",
		# )
		# st.plotly_chart(fig, use_container_width=True)
'''				







































