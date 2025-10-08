import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def home():
	st.title("Home")

def archivos():
	st.title("Archivos")
	uploaded_file = st.file_uploader("Elige un archivo CSV", type='csv')
	corriente_carga = st.number_input("Introduce la corriente de carga:")
	corriente_descarga = st.number_input("Introduce la corriente de descarga:")
	if uploaded_file is not None:	
		datos=pd.read_csv(uploaded_file)
		datos["Time1(h)"]=datos["DataPoint"]*10/3600
		datos["Capacity1(mAh/cm2)"]=datos["Capacity(mAh)"]/(np.pi*4**2)

		# plt.plot(datos["DataPoint"],datos["Voltage(V)"])
		fig=px.line( datos, "DataPoint",y=["Voltage(V)", "Current(mA)"])
		# fig=px.line(datos, x="Capacity(Ah)",y="Voltage(V)")
		fig.layout.title="Voltaje vs DataPoint"
		st.plotly_chart(fig, use_container_width=True)

		datos["Paso"]=""
		print (datos.keys())
		k_carga = 1
		k_descarga = 1

		

		for i in range(len(datos)):
			current = datos.loc[i, "Current(mA)"]

			if current == 0:
				datos.loc[i, "Paso"] = "Rest"
			elif current >= corriente_carga:
				datos.loc[i, "Paso"] = f"Carga {k_carga}"
				# Si el siguiente valor cambia de signo o a cero, pasamos al siguiente ciclo
				if i < len(datos) - 1 and datos.loc[i+1, "Current(mA)"] <= 0:
					k_carga += 1
			elif current <= corriente_descarga:
				datos.loc[i, "Paso"] = f"Descarga {k_descarga}"
				if i < len(datos) - 1 and datos.loc[i+1, "Current(mA)"] >= 0:
					k_descarga += 1
		
		
		fig1=px.line( datos, "Capacity1(mAh/cm2)", "Voltage(V)",color="Paso")
		st.plotly_chart(fig1, use_container_width=True)
