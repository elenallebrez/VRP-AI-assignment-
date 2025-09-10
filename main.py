import pandas as pd
from src.utils import cargar_datos
from src.knn_assignment import asignar_oficinas
from src.graph_utils import construir_grafo_desde_csv
from src.reparto import repartir_todos_los_paquetes

if __name__ == "__main__":

    paquetes, vehicules, oficinas_coordenadas, distancias_ciudades = cargar_datos()

    print("Datos cargados correctamente.")
    print(f"- Paquetes: {len(paquetes)}")
    print(f"- Vehículos: {len(vehicules)}")
    print(f"- Oficinas: {len(oficinas_coordenadas)}\n")

    # 2. Asignar oficinas a los paquetes
    packaging = asignar_oficinas(paquetes, oficinas_coordenadas)
    print("Oficinas asignadas a los paquetes (ejemplo):")
    print(packaging[['id', 'destino', 'oficina_asignada']].head(), "\n")

    # 3. Crear grafo de distancias
    grafo = construir_grafo_desde_csv(distancias_ciudades)

    # 4. 🚚 Reparto por rondas
    resultados = repartir_todos_los_paquetes(vehicules, packaging, grafo)

    # 5. Mostrar resultados
    print("\n===== RESULTADOS DEL REPARTO =====")
    df_resultados = pd.DataFrame(resultados)
    print(df_resultados)

    # Métricas globales
    print("\n--- MÉTRICAS ---")
    print(f"Distancia total recorrida: {df_resultados['distancia'].sum():.2f} km")
    print(f"Total de rondas realizadas: {df_resultados['ronda'].max()}")
    print(f"Paquetes entregados: {sum(len(x) for x in df_resultados['paquetes_entregados'])} / {len(packaging)}")
