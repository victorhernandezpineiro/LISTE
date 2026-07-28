import streamlit as st
import h5py
import numpy as np
import matplotlib.pyplot as plt
import math

def ratiohdf5():

    st.title("Visualizador de mapas EDS")

    # ==========================================================
    # Tabla de energías
    # ==========================================================

    ELEMENTS = {
        "C": 277,
        "N": 392,
        "O": 525,
        "F": 677,
        "Na": 1041,
        "Mg": 1254,
        "Al": 1487,
        "Si": 1740,
        "P": 2013,
        "S": 2307,
        "Cl": 2622,
        "K": 3312,
        "Ca": 3690,
        "Ti": 4511,
        "V": 4952,
        "Cr": 5414,
        "Mn": 5899,
        "Fe": 6404,
        "Co": 6930,
        "Ni": 7478,
        "Cu": 8048,
        "Zn": 8638
    }

    # ==========================================================
    # Función
    # ==========================================================

    def element_map(spectra, energy, peak, window):

        idx = np.where(
            (energy >= peak-window) &
            (energy <= peak+window)
        )[0]

        return spectra[:, :, idx].sum(axis=2)

    # ==========================================================
    # Cargar archivo
    # ==========================================================

    archivo = st.file_uploader(
        "Selecciona un archivo HDF5",
        type=["hdf5", "h5"]
    )

    if archivo is None:
        return

    with h5py.File(archivo, "r") as f:

        spectra = f["spectra"][:]
        energy = f["energy_axis"][:]

    st.success(f"Cubo cargado correctamente: {spectra.shape}")

    st.divider()

    # ==========================================================
    # Parámetros
    # ==========================================================

    elementos = st.multiselect(
        "Selecciona los elementos",
        list(ELEMENTS.keys()),
        default=["C", "O"]
    )

    window = st.slider(
        "Ventana de integración (± eV)",
        20,
        200,
        80
    )

    # ==========================================================
    # Generación
    # ==========================================================

    if not st.button("Generar mapas"):
        return

    if len(elementos) == 0:
        st.warning("Selecciona al menos un elemento.")
        return

    mapas = {}

    with st.spinner("Calculando mapas..."):

        for elemento in elementos:

            mapas[elemento] = element_map(
                spectra,
                energy,
                ELEMENTS[elemento],
                window
            )

    st.success("Mapas generados correctamente.")

    # ==========================================================
    # Visualización
    # ==========================================================

    st.divider()
    st.subheader("Opciones de visualización")

    modo = st.radio(
        "Escala",
        ["Automática", "Manual"],
        horizontal=True
    )

    cmap = st.selectbox(
        "Mapa de colores",
        [
            "inferno",
            "viridis",
            "plasma",
            "magma",
            "gray",
            "hot",
            "jet"
        ]
    )

    max_global = int(max(np.max(m) for m in mapas.values()))

    if modo == "Manual":

        col1, col2 = st.columns(2)

        with col1:
            vmin = st.slider(
                "Valor mínimo",
                0,
                max_global,
                0
            )

        with col2:
            vmax = st.slider(
                "Valor máximo",
                max(vmin + 1, 1),
                max_global,
                max_global
            )

    # ==========================================================
    # Mapas individuales
    # ==========================================================

    st.header("Mapas individuales")

    for elemento in elementos:

        fig, ax = plt.subplots(figsize=(6,6))

        kwargs = dict(
            cmap=cmap,
            origin="lower"
        )

        if modo == "Manual":
            kwargs["vmin"] = vmin
            kwargs["vmax"] = vmax

        im = ax.imshow(
            mapas[elemento],
            **kwargs
        )

        ax.set_title(elemento)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        plt.colorbar(im, ax=ax, label="Cuentas")

        st.pyplot(fig)

        plt.close(fig)

    # ==========================================================
    # Figura conjunta
    # ==========================================================

    st.header("Todos los elementos")

    n = len(elementos)

    cols = min(3, n)
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(6*cols, 6*rows)
    )

    if n == 1:
        axes = np.array([axes])

    axes = axes.flatten()

    for ax, elemento in zip(axes, elementos):

        kwargs = dict(
            cmap=cmap,
            origin="lower"
        )

        if modo == "Manual":
            kwargs["vmin"] = vmin
            kwargs["vmax"] = vmax

        im = ax.imshow(
            mapas[elemento],
            **kwargs
        )

        ax.set_title(elemento)

        plt.colorbar(
            im,
            ax=ax,
            fraction=0.046,
            pad=0.04,
            label="Cuentas"
        )

    for ax in axes[n:]:
        fig.delaxes(ax)

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)
