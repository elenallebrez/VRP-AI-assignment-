import pandas as pd

from src.graph_utils import construir_grafo_desde_csv
from src.knn_assignment import asignar_oficinas
from src.reparto import repartir_todos_los_paquetes
from src.utils import cargar_datos


if __name__ == "__main__":
    paquetes, vehiculos, oficinas_coordenadas, distancias_ciudades = cargar_datos()

    print("Datos cargados correctamente.")
    print(f"- Paquetes: {len(paquetes)}")
    print(f"- Vehiculos: {len(vehiculos)}")
    print(f"- Oficinas: {len(oficinas_coordenadas)}\n")

    paquetes_asignados = asignar_oficinas(paquetes, oficinas_coordenadas)
    print("Oficinas asignadas a los paquetes (ejemplo):")
    print(paquetes_asignados[["id", "destino", "oficina_asignada"]].head(), "\n")

    grafo = construir_grafo_desde_csv(distancias_ciudades)
    resultados = repartir_todos_los_paquetes(vehiculos, paquetes_asignados, grafo)

    print("\n===== RESULTADOS DEL REPARTO =====")
    df_resultados = pd.DataFrame(resultados)
    print(df_resultados)

    print("\n--- METRICAS ---")
    print(f"Distancia total recorrida: {df_resultados['distancia'].sum():.2f} km")
    print(f"Total de rondas realizadas: {df_resultados['ronda'].max()}")
    print(
        "Paquetes entregados: "
        f"{sum(len(x) for x in df_resultados['paquetes_entregados'])} / {len(paquetes_asignados)}"
    )
