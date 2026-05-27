from src.genetic_vrp import ProblemGeneticVRP, genetic_algorithm


def repartir_todos_los_paquetes(vehiculos, paquetes, grafo):
    """
    Planifica el reparto completo con algoritmo genetico.

    KNN debe haberse ejecutado antes para crear `oficina_asignada`.
    El AG decide que paquetes atiende cada camion y en que orden.
    """
    if "oficina_asignada" not in paquetes.columns:
        raise ValueError("Falta la columna 'oficina_asignada'. Ejecuta KNN antes del reparto.")

    problem = ProblemGeneticVRP(paquetes.copy(), vehiculos.copy(), grafo)
    result = genetic_algorithm(problem)

    delivered = sum(len(route["paquetes_entregados"]) for route in result.plan)
    if delivered != len(paquetes):
        raise RuntimeError(
            f"El plan genetico no entrego todos los paquetes: {delivered}/{len(paquetes)}"
        )

    return result.plan
