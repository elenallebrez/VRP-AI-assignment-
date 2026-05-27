import pandas as pd

def construir_grafo_desde_csv(distances_df: pd.DataFrame):
    graph = {}
    
    for _, row in distances_df.iterrows():
        origen = str(row['origen']).strip().lower()
        destino = str(row['destino']).strip().lower()
        distancia = row['Distance(km)']
        
        if origen not in graph:
            graph[origen] = {}
        if destino not in graph:
            graph[destino] = {}

        graph[origen][destino] = distancia
        graph[destino][origen] = distancia  # grafo simétrico

    return graph


def shortest_path(graph, origin, destination):
    if origin not in graph or destination not in graph:
        return None

    distances = {city: float('inf') for city in graph}
    distances[origin] = 0
    visited = set()
    
    while True:
        # Encontrar el nodo no visitado con menor distancia
        current_node = None
        current_dist = float('inf')
        for node in graph:
            if node not in visited and distances[node] < current_dist:
                current_node = node
                current_dist = distances[node]

        if current_node is None:
            break  # Todos los nodos visitados o inalcanzables

        if current_node == destination:
            return distances[current_node]

        visited.add(current_node)

        for neighbor, weight in graph[current_node].items():
            if neighbor in visited:
                continue
            new_dist = distances[current_node] + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist

    return None


def shortest_path_route(graph, origin, destination):
    if origin not in graph or destination not in graph:
        return None

    distances = {city: float('inf') for city in graph}
    previous = {city: None for city in graph}
    distances[origin] = 0
    visited = set()

    while True:
        current_node = None
        current_dist = float('inf')
        for node in graph:
            if node not in visited and distances[node] < current_dist:
                current_node = node
                current_dist = distances[node]

        if current_node is None:
            break  # Todos los nodos visitados o inalcanzables

        if current_node == destination:
            break

        visited.add(current_node)

        for neighbor, weight in graph[current_node].items():
            if neighbor in visited:
                continue
            new_dist = distances[current_node] + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current_node

    path = []
    current = destination
    while current is not None:
        path.insert(0, current)
        current = previous[current]

    if path and path[0] == origin:
        return path
    return None
