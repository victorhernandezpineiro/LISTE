import streamlit as st
import pandas as pd
import plotly.express as px

def home():
	st.title("Home")

def archivos():
	st.title("Archivos")
	uploaded_file = st.file_uploader("Elige un archivo CSV", type='csv')

	if uploaded_file is not None:
		datos=pd.read_csv(uploaded_file)
		datos["Time1(h)"]=datos["DataPoint"]*10/3600
		datos["Capacity1(mAh)"]=datos["Energy(Wh)"]/datos["Voltage(V)"]*1000
		# plt.plot(datos["DataPoint"],datos["Voltage(V)"])
		fig=px.line( datos, "DataPoint",y=["Voltage(V)", "Capacity(mAh)"])
		# fig=px.line(datos, x="Capacity(Ah)",y="Voltage(V)")
		fig.layout.title="Voltaje vs DataPoint"
		st.plotly_chart(fig, use_container_width=True)
		 
		fig1=px.line( datos, "Time1(h)","Capacity1(mAh)")
		st.plotly_chart(fig1, use_container_width=True)
