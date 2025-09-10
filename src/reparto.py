from collections import defaultdict
import pandas as pd
from src.genetic_vrp import ProblemGeneticVRP, genetic_algorithm
from src.graph_utils import shortest_path, shortest_path_route

def repartir_todos_los_paquetes(vehicules, packaging, grafo):
    vehicules = vehicules.copy()
    packaging['entregado'] = False
    resultados = []
    rondas = defaultdict(int)

    while not packaging['entregado'].all():
        for i, camion in vehicules.iterrows():
            camion_id = camion['id']
            ciudad_actual = vehicules.at[i, 'initial'].lower()
            ciudad_inicio_real = ciudad_actual
            ruta_extra = []

            # Buscar paquetes en ciudad actual
            disponibles = packaging[
                (packaging['entregado'] == False) &
                (packaging['oficina_asignada'].str.lower() == ciudad_actual)
            ]

            # Si no hay paquetes, buscar la ciudad más cercana con paquetes
            if disponibles.empty:
                ciudades_con_paquetes = packaging[
                    packaging['entregado'] == False
                ]['oficina_asignada'].str.lower().unique()

                if not len(ciudades_con_paquetes):
                    continue

                distancias = [
                    (ciudad, shortest_path(grafo, ciudad_actual, ciudad))
                    for ciudad in ciudades_con_paquetes
                    if shortest_path(grafo, ciudad_actual, ciudad) is not None
                ]
                if not distancias:
                    continue

                ciudad_mas_cercana = min(distancias, key=lambda x: x[1])[0]
                camino_extra = shortest_path_route(grafo, ciudad_actual, ciudad_mas_cercana)

                if camino_extra:
                    ruta_extra = camino_extra[1:]
                    ciudad_actual = ciudad_mas_cercana
                    vehicules.at[i, 'initial'] = ciudad_actual

                disponibles = packaging[
                    (packaging['entregado'] == False) &
                    (packaging['oficina_asignada'].str.lower() == ciudad_actual)
                ]

            disponibles = disponibles.sort_values(by='prioridad', ascending=True)

            # Selección de paquetes
            seleccionados = []
            capacidad = camion['size']
            for _, paquete in disponibles.iterrows():
                if paquete['size'] <= capacidad:
                    seleccionados.append(paquete)
                    capacidad -= paquete['size']

            if not seleccionados:
                continue

            df_seleccionados = pd.DataFrame(seleccionados)

            # Ruta con algoritmo genético
            tsp = ProblemGeneticVRP(df_seleccionados, ciudad_actual, grafo)
            ruta, _ = genetic_algorithm(tsp)

            # Construcción de la ruta completa y cálculo realista de distancia
            actual = ciudad_inicio_real
            ruta_completa = [actual]
            distancia_total = 0

            # Agregar ruta_extra (hasta llegar a ciudad_actual)
            for ciudad in ruta_extra:
                camino = shortest_path_route(grafo, actual, ciudad)
                if camino is None or len(camino) < 2:
                    continue
                for j in range(1, len(camino)):
                    distancia_total += shortest_path(grafo, camino[j - 1], camino[j])
                ruta_completa.extend(camino[1:])
                actual = ciudad

            # Ruta de reparto (con paquetes)
            for destino in ruta:
                camino = shortest_path_route(grafo, actual, destino)
                if camino is None or len(camino) < 2:
                    continue
                for j in range(1, len(camino)):
                    distancia_total += shortest_path(grafo, camino[j - 1], camino[j])
                ruta_completa.extend(camino[1:])
                actual = destino

            # Eliminar ciudades duplicadas consecutivas
            ruta_sin_repetidos = [ruta_completa[0]]
            for ciudad in ruta_completa[1:]:
                if ciudad != ruta_sin_repetidos[-1]:
                    ruta_sin_repetidos.append(ciudad)

            # Actualizar estado
            vehicules.at[i, 'initial'] = actual
            packaging.loc[packaging['id'].isin(df_seleccionados['id']), 'entregado'] = True

            rondas[camion_id] += 1
            resultados.append({
                'camion_id': camion_id,
                'ronda': rondas[camion_id],
                'ciudad_inicio': ciudad_inicio_real,
                'paquetes_entregados': df_seleccionados['id'].tolist(),
                'ruta': ruta_sin_repetidos,
                'distancia': distancia_total
            })

    return resultados