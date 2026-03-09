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
			x_col = st.selectbox("📈 Eje X:", datos.columns.tolist(), index=0)
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
						   color="Tipo Paso", title="Capacidad Específica por Paso")
			fig1.update_traces(line=dict(width=3))
			st.plotly_chart(fig1, use_container_width=True)



































