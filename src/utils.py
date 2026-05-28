from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


def convertir_a_float(columna: pd.Series) -> pd.Series:
    """Convierte strings con coma decimal a float."""
    return columna.astype(str).str.replace(",", ".", regex=False).astype(float)


def cargar_datos(data_dir=DEFAULT_DATA_DIR):
    """
    Carga los CSV del proyecto.

    `data_dir` permite ejecutar el proyecto desde cualquier directorio.
    """
    data_dir = Path(data_dir)

    paquetes = pd.read_csv(
        data_dir / "paquetes.csv",
        header=0,
        names=["id", "size", "prioridad", "destino", "latitud", "longitud"],
    )
    vehiculos = pd.read_csv(
        data_dir / "vehiculos_csv.csv",
        header=0,
        names=["id", "size", "initial"],
    )
    oficinas_coordenadas = pd.read_csv(
        data_dir / "ciudades_coordenadas.csv",
        header=0,
        names=["ciudad", "latitud", "longitud"],
    )
    distancias_ciudades = pd.read_csv(
        data_dir / "distancia_ciudades.csv",
        header=0,
        names=["origen", "destino", "Distance(km)"],
    )

    paquetes["latitud"] = convertir_a_float(paquetes["latitud"])
    paquetes["longitud"] = convertir_a_float(paquetes["longitud"])
    oficinas_coordenadas["latitud"] = convertir_a_float(oficinas_coordenadas["latitud"])
    oficinas_coordenadas["longitud"] = convertir_a_float(oficinas_coordenadas["longitud"])

    vehiculos["initial"] = vehiculos["initial"].astype(str).str.strip().str.lower()
    oficinas_coordenadas["ciudad"] = oficinas_coordenadas["ciudad"].astype(str).str.strip().str.lower()
    paquetes["destino"] = paquetes["destino"].astype(str).str.strip().str.lower()

    if "oficina_asignada" in paquetes.columns:
        paquetes["oficina_asignada"] = paquetes["oficina_asignada"].astype(str).str.strip().str.lower()

    return paquetes, vehiculos, oficinas_coordenadas, distancias_ciudades
