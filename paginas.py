import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def home():
	st.title("Home")

def archivos():
	st.title("Archivos")
	uploaded_file = st.file_uploader("Elige un archivo CSV", type='csv')
	# corriente_carga = st.number_input("Introduce la corriente de carga:")
	# corriente_descarga = st.number_input("Introduce la corriente de descarga:")
	if uploaded_file is not None:	
		datos=pd.read_csv(uploaded_file,encoding="latin1")
		st.write("### 📋 Datos")
		datos["Time1(h)"]=datos["DataPoint"]*10/3600
		for i in range(len(datos)):
			if datos.loc[i, "Step Type"] == "CV Chg":
				datos.loc[i, "Capacity1(microAh/cm2)"] = datos.loc[i, "Capacity(mAh)"]*1000 / (np.pi * 4**2) + datos.loc[i - 1, "Capacity1(microAh/cm2)"]
			else:
				datos.loc[i, "Capacity1(microAh/cm2)"] = datos.loc[i, "Capacity(mAh)"]*1000 / (np.pi * 4**2)


		if "Current(mA)" in datos.columns or "Current(µA)" in datos.columns:
			current_col = "Current(mA)" if "Current(mA)" in datos.columns else "Current(µA)"
			datos["Paso"] = ""
			k_carga = 1
			k_descarga = 1
			for i in range(len(datos)):
				current = datos.loc[i, current_col]
				if current == 0:
					datos.loc[i, "Paso"] = "Rest"
				elif current > 0:
					datos.loc[i, "Paso"] = f"Charge {k_carga}"
					if i < len(datos) - 1 and datos.loc[i + 1, current_col] <= 0:
						k_carga += 1
				else:
					datos.loc[i, "Paso"] = f"Discharge {k_descarga}"
					if i < len(datos) - 1 and datos.loc[i + 1, current_col] >= 0:
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

		datos["Paso"]=""
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

			if current == 0:
				datos.loc[i, "Paso"] = "Rest"
			elif current > 0:
				datos.loc[i, "Paso"] = f"Charge {k_carga}"
				# Si el siguiente valor cambia de signo o a cero, pasamos al siguiente ciclo
				if i < len(datos) - 1 and datos.loc[i+1, columnname] <= 0:
					k_carga += 1
			elif current < 0:
				datos.loc[i, "Paso"] = f"Discharge {k_descarga}"
				if i < len(datos) - 1 and datos.loc[i+1, columnname] >= 0:
					k_descarga += 1
		
		
		fig1=px.line( datos, "Capacity1(microAh/cm2)", "Voltage(V)",color="Paso")
		st.plotly_chart(fig1, use_container_width=True)


		capacidad_max = []

		for i in range(1, len(datos)):  # empieza en 1 para poder usar i-1
			if datos.loc[i, "Paso"] != datos.loc[i - 1, "Paso"]:
				capacidad_max.append([
					datos.loc[i-1, "DataPoint"],
					datos.loc[i - 1, "Paso"],
					datos.loc[i - 1, "Capacity1(microAh/cm2)"]
				])
			elif i == len(datos) - 1:  # último punto
				capacidad_max.append([
					datos.loc[i, "DataPoint"],
					datos.loc[i, "Paso"],
					datos.loc[i, "Capacity1(microAh/cm2)"]
				])
		df1= pd.DataFrame(capacidad_max, columns=["DataPoint", "Ciclo", "Capacidad máxima (microAh/cm2)"])
		st.dataframe(df1)

		# --- 2️⃣ Calcular eficiencia (Descarga/Carga * 100) ---
		# Extraer el tipo de paso (Carga o Descarga) y número de ciclo
		df1["Tipo"] = df1["Ciclo"].str.extract(r'(Charge|Discharge)', expand=False)
		df1["Nº ciclo"] = df1["Ciclo"].str.extract(r'(\d+)', expand=False).astype(float)

		# Pivotar la tabla para tener columnas separadas
		tabla_ef = df1.pivot_table(
			index="Nº ciclo",
			columns="Tipo",
			values="Capacidad máxima (microAh/cm2)",
			aggfunc="first"
		).reset_index()

		# Calcular la eficiencia
		tabla_ef["Eficiencia (%)"] = (tabla_ef["Discharge"] / tabla_ef["Charge"]) * 100

		st.subheader("⚙️ Eficiencia coulombica")
		st.dataframe(tabla_ef, use_container_width=True)

		soh=[]
		for i in range (1,len(df1)):
			soh_i=tabla_ef.loc[i,"Discharge"]/tabla_ef.loc[0,"Discharge"]*100
			soh.append([i,soh_i])
		df2= pd.DataFrame(capacidad_max, columns=["Cycle", "SOH"])
		st.dataframe(df2)

			

		# # --- 3️⃣ (Opcional) Representar gráficamente ---
		# import plotly.express as px

		# fig = px.bar(
		# 	tabla_ef,
		# 	x="Nº ciclo",
		# 	y="Eficiencia (%)",
		# 	title="Eficiencia de descarga/carga por ciclo",
		# )
		# st.plotly_chart(fig, use_container_width=True)

				

			







