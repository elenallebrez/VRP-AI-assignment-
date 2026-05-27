import pandas as pd
from sklearn.neighbors import KNeighborsClassifier


def _validar_columnas(df: pd.DataFrame, columnas: set[str], nombre: str) -> None:
    faltantes = columnas - set(df.columns)
    if faltantes:
        raise ValueError(f"{nombre} no contiene las columnas requeridas: {sorted(faltantes)}")


def _validar_coordenadas(df: pd.DataFrame, columnas: list[str], nombre: str) -> None:
    if df[columnas].isnull().any().any():
        raise ValueError(f"{nombre} contiene coordenadas nulas.")


def asignar_oficinas(paquetes: pd.DataFrame, oficinas_coordenadas: pd.DataFrame, k: int = 1) -> pd.DataFrame:
    """
    Asigna cada paquete a la oficina mas cercana usando KNN con k=1.

    En este proyecto, KNN se usa como nearest-office assignment:
    `oficina_asignada` representa la oficina/delegacion de recogida.
    """
    _validar_columnas(paquetes, {"latitud", "longitud"}, "paquetes")
    _validar_columnas(oficinas_coordenadas, {"ciudad", "latitud", "longitud"}, "oficinas_coordenadas")
    _validar_coordenadas(paquetes, ["latitud", "longitud"], "paquetes")
    _validar_coordenadas(oficinas_coordenadas, ["latitud", "longitud"], "oficinas_coordenadas")

    if k != 1:
        raise ValueError("Este proyecto usa k=1 para asignar la oficina mas cercana.")

    oficinas = oficinas_coordenadas.copy()
    oficinas["ciudad"] = oficinas["ciudad"].astype(str).str.strip().str.upper()

    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(oficinas[["latitud", "longitud"]], oficinas["ciudad"])

    paquetes = paquetes.copy()
    paquetes["oficina_asignada"] = knn.predict(paquetes[["latitud", "longitud"]])
    paquetes["oficina_asignada"] = paquetes["oficina_asignada"].astype(str).str.strip().str.upper()

    return paquetes
