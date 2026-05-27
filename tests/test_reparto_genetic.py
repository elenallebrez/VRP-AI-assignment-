import pandas as pd
import pytest

from src.genetic_vrp import ProblemGeneticVRP, genetic_algorithm
from src.graph_utils import construir_grafo_desde_csv
from src.knn_assignment import asignar_oficinas
from src.reparto import repartir_todos_los_paquetes
from src.utils import cargar_datos


def test_reparto_entrega_todos_los_paquetes_actuales():
    paquetes, vehiculos, oficinas, distancias = cargar_datos()
    paquetes = asignar_oficinas(paquetes, oficinas)
    grafo = construir_grafo_desde_csv(distancias)

    resultados = repartir_todos_los_paquetes(vehiculos, paquetes, grafo)
    entregados = sorted(package_id for ruta in resultados for package_id in ruta["paquetes_entregados"])

    assert entregados == list(range(1, len(paquetes) + 1))


def test_genetic_algorithm_is_reproducible_with_seed():
    paquetes, vehiculos, oficinas, distancias = cargar_datos()
    paquetes = asignar_oficinas(paquetes, oficinas)
    grafo = construir_grafo_desde_csv(distancias)
    problem = ProblemGeneticVRP(paquetes, vehiculos, grafo)

    first = genetic_algorithm(problem, population_size=20, generations=20, seed=7)
    second = genetic_algorithm(problem, population_size=20, generations=20, seed=7)

    assert first.total_distance == second.total_distance
    assert first.plan == second.plan


def test_package_too_large_raises_clear_error():
    paquetes = pd.DataFrame(
        {
            "id": [1],
            "size": [99],
            "prioridad": [1],
            "destino": ["madrid"],
            "oficina_asignada": ["madrid"],
        }
    )
    vehiculos = pd.DataFrame({"id": [1], "size": [1], "initial": ["madrid"]})
    grafo = {"madrid": {}}
    problem = ProblemGeneticVRP(paquetes, vehiculos, grafo)

    with pytest.raises(ValueError, match="no caben"):
        genetic_algorithm(problem)
