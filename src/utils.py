import pandas as pd

def convertir_a_float(col: pd.Series) -> pd.Series:
    """
    Convierte una columna de strings con comas decimales a float.
    """
    return col.astype(str).str.replace(',', '.', regex=False).astype(float)


def cargar_datos():
    """
    Carga los datos desde la carpeta 'data' y devuelve los DataFrames procesados.

    Retorna
    -------
    paquetes : pd.DataFrame
        Paquetes con columnas ['id', 'size', 'prioridad', 'destino', 'latitud', 'longitud'].
    vehicules : pd.DataFrame
        Vehículos con columnas ['id', 'size', 'initial'].
    oficinas_coordenadas : pd.DataFrame
        Oficinas con columnas ['ciudad', 'latitud', 'longitud'].
    distancias_ciudades : pd.DataFrame
        Distancias entre ciudades con columnas ['origen', 'destino', 'Distance(km)'].
    """
    # Cargar CSVs
    paquetes = pd.read_csv(
        "data/paquetes.csv",
        header=0,
        names=['id', 'size', 'prioridad', 'destino', 'latitud', 'longitud']
    )

    vehicules = pd.read_csv(
        "data/vehiculos_csv.csv",
        header=0,
        names=['id', 'size', 'initial']
    )

    oficinas_coordenadas = pd.read_csv(
        "data/ciudades_coordenadas.csv",
        header=0,
        names=['ciudad', 'latitud', 'longitud']
    )

    distancias_ciudades = pd.read_csv(
        "data/distancia_ciudades.csv",
        header=0,
        names=['origen', 'destino', 'Distance(km)']
    )

    # Conversión de coordenadas
    paquetes['latitud'] = convertir_a_float(paquetes['latitud'])
    paquetes['longitud'] = convertir_a_float(paquetes['longitud'])
    oficinas_coordenadas['latitud'] = convertir_a_float(oficinas_coordenadas['latitud'])
    oficinas_coordenadas['longitud'] = convertir_a_float(oficinas_coordenadas['longitud'])

    # Normalización de strings a minúsculas y sin espacios
    vehicules['initial'] = vehicules['initial'].astype(str).str.strip().str.lower()
    oficinas_coordenadas['ciudad'] = oficinas_coordenadas['ciudad'].astype(str).str.strip().str.lower()
    paquetes['destino'] = paquetes['destino'].astype(str).str.strip().str.lower()

    if 'oficina_asignada' in paquetes.columns:
        paquetes['oficina_asignada'] = paquetes['oficina_asignada'].astype(str).str.strip().str.lower()

    return paquetes, vehicules, oficinas_coordenadas, distancias_ciudades
