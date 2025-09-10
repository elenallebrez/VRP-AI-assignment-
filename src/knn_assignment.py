import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

def asignar_oficinas(packaging: pd.DataFrame, oficinas_coordenadas: pd.DataFrame, k: int = 1) -> pd.DataFrame:
    """
    Asigna cada paquete a la oficina más cercana usando KNN.
    Compatible con el grafo de graph_utils y normalizado para evitar KeyErrors.

    Parámetros
    ----------
    packaging : pd.DataFrame
        DataFrame con columnas ['latitud', 'longitud'] de los paquetes.
    oficinas_coordenadas : pd.DataFrame
        DataFrame con columnas ['latitud', 'longitud', 'ciudad'] de las oficinas.
    k : int, opcional
        Número de vecinos a considerar en KNN. Default=1.

    Retorna
    -------
    packaging : pd.DataFrame
        DataFrame con nueva columna 'oficina_asignada' en mayúsculas.
    """
    # Normalizar nombres de oficinas (compatibles con utils)
    oficinas_coordenadas = oficinas_coordenadas.copy()
    oficinas_coordenadas['ciudad'] = oficinas_coordenadas['ciudad'].astype(str).str.strip().str.upper()

    # Entrenar KNN con coordenadas de oficinas
    X_train = oficinas_coordenadas[['latitud', 'longitud']]
    y_train = oficinas_coordenadas['ciudad']
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)

    # Predecir oficina para cada paquete
    X_test = packaging[['latitud', 'longitud']]
    packaging = packaging.copy()
    packaging['oficina_asignada'] = knn.predict(X_test)

    # Normalizar resultado para que coincida con graph_utils (en minúsculas solo al usar rutas)
    packaging['oficina_asignada'] = packaging['oficina_asignada'].astype(str).str.strip().str.upper()

    return packaging
