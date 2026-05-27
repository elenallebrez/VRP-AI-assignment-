import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.graph_utils import shortest_path, shortest_path_route


@dataclass(frozen=True)
class Package:
    id: int
    size: int
    priority: int
    pickup: str
    destination: str


@dataclass(frozen=True)
class Vehicle:
    index: int
    id: int
    capacity: int
    initial_city: str


@dataclass(frozen=True)
class GeneticResult:
    best_chromosome: List[List[int]]
    plan: List[dict]
    total_distance: float
    fitness_cost: float


class ProblemGeneticVRP:
    """
    VRP abierto con recogida dinamica.

    Un cromosoma es una lista de rutas, una por vehiculo. Cada ruta contiene
    IDs de paquetes. El algoritmo genetico decide que paquetes atiende cada
    camion y en que orden se intentan recoger/entregar.
    """

    INVALID_ROUTE_PENALTY = 1_000_000
    UNDELIVERED_PACKAGE_PENALTY = 100_000

    def __init__(self, paquetes_df: pd.DataFrame, vehiculos_df: pd.DataFrame, grafo):
        self.graph = grafo
        self.packages = self._build_packages(paquetes_df)
        self.vehicles = self._build_vehicles(vehiculos_df)
        self.package_ids = list(self.packages.keys())
        self.compatible_vehicles = self._build_compatible_vehicles()
        self.distance_cache: Dict[Tuple[str, str], Optional[float]] = {}
        self.route_cache: Dict[Tuple[str, str], Optional[List[str]]] = {}
        self._precompute_relevant_paths()

    def create_chromosome(self, rng: random.Random) -> List[List[int]]:
        routes = [[] for _ in self.vehicles]
        package_ids = self.package_ids[:]
        rng.shuffle(package_ids)

        for package_id in package_ids:
            vehicle_index = rng.choice(self.compatible_vehicles[package_id])
            routes[vehicle_index].append(package_id)

        for route in routes:
            rng.shuffle(route)

        return routes

    def decode(self, chromosome: List[List[int]]) -> List[dict]:
        plan, _, _, _ = self.evaluate(chromosome)
        return plan

    def fitness(self, chromosome: List[List[int]]) -> float:
        _, _, fitness_cost, is_valid = self.evaluate(chromosome)
        if not is_valid:
            fitness_cost += self.INVALID_ROUTE_PENALTY
        return -fitness_cost

    def evaluate(self, chromosome: List[List[int]]) -> Tuple[List[dict], float, float, bool]:
        plan = []
        delivered = set()
        total_distance = 0.0
        fitness_cost = 0.0
        is_valid = True

        for vehicle, route in zip(self.vehicles, chromosome):
            vehicle_plan, delivered_ids, route_distance, route_priority_cost, route_is_valid = self._simulate_vehicle_route(
                vehicle,
                route,
                len(delivered),
            )
            total_distance += route_distance
            fitness_cost += route_distance + route_priority_cost
            is_valid = is_valid and route_is_valid

            duplicated = delivered.intersection(delivered_ids)
            if duplicated:
                fitness_cost += len(duplicated) * self.INVALID_ROUTE_PENALTY
                is_valid = False

            delivered.update(delivered_ids)
            if vehicle_plan["paquetes_entregados"]:
                plan.append(vehicle_plan)

        missing_packages = set(self.package_ids) - delivered
        if missing_packages:
            fitness_cost += len(missing_packages) * self.UNDELIVERED_PACKAGE_PENALTY
            is_valid = False

        return plan, total_distance, fitness_cost, is_valid

    def crossover(
        self,
        parent_a: List[List[int]],
        parent_b: List[List[int]],
        rng: random.Random,
    ) -> Tuple[List[List[int]], List[List[int]]]:
        order_a = self._flatten(parent_a)
        order_b = self._flatten(parent_b)
        child_order_a = self._ordered_crossover(order_a, order_b, rng)
        child_order_b = self._ordered_crossover(order_b, order_a, rng)

        assignments_a = self._route_assignments(parent_a)
        assignments_b = self._route_assignments(parent_b)

        return (
            self._build_child(child_order_a, assignments_a, assignments_b, rng),
            self._build_child(child_order_b, assignments_b, assignments_a, rng),
        )

    def mutation(
        self,
        chromosome: List[List[int]],
        mutation_prob: float,
        rng: random.Random,
    ) -> List[List[int]]:
        mutated = [route[:] for route in chromosome]

        if rng.random() < mutation_prob:
            self._mutate_swap(mutated, rng)

        if rng.random() < mutation_prob:
            self._mutate_move_between_vehicles(mutated, rng)

        if rng.random() < mutation_prob:
            self._mutate_reverse_segment(mutated, rng)

        return mutated

    def validate_inputs(self) -> None:
        if not self.packages:
            raise ValueError("No hay paquetes para repartir.")
        if not self.vehicles:
            raise ValueError("No hay vehiculos disponibles.")

        invalid_packages = [
            package.id
            for package in self.packages.values()
            if not self.compatible_vehicles[package.id]
        ]
        if invalid_packages:
            raise ValueError(
                "Hay paquetes que no caben en ningun vehiculo: "
                f"{invalid_packages}"
            )

        missing_cities = sorted(
            {
                city
                for package in self.packages.values()
                for city in (package.pickup, package.destination)
                if city not in self.graph
            }
            | {
                vehicle.initial_city
                for vehicle in self.vehicles
                if vehicle.initial_city not in self.graph
            }
        )
        if missing_cities:
            raise ValueError(f"Ciudades ausentes en el grafo: {missing_cities}")

    def _simulate_vehicle_route(
        self,
        vehicle: Vehicle,
        route: List[int],
        delivered_before_route: int,
    ) -> Tuple[dict, List[int], float, float, bool]:
        current_city = vehicle.initial_city
        full_route = [current_city]
        delivered_ids = []
        total_distance = 0.0
        priority_penalty = 0.0
        is_valid = True
        i = 0

        while i < len(route):
            package = self.packages[route[i]]

            if package.size > vehicle.capacity:
                is_valid = False
                i += 1
                continue

            distance_to_pickup = self._distance(current_city, package.pickup)
            path_to_pickup = self._route(current_city, package.pickup)
            if distance_to_pickup is None or path_to_pickup is None:
                is_valid = False
                i += 1
                continue

            total_distance += distance_to_pickup
            full_route.extend(path_to_pickup[1:])
            current_city = package.pickup

            load, i = self._load_consecutive_packages(route, i, package.pickup, vehicle.capacity)

            for loaded_package in load:
                distance_to_destination = self._distance(current_city, loaded_package.destination)
                path_to_destination = self._route(current_city, loaded_package.destination)
                if distance_to_destination is None or path_to_destination is None:
                    is_valid = False
                    continue

                total_distance += distance_to_destination
                priority_penalty += loaded_package.priority * (delivered_before_route + len(delivered_ids) + 1)
                full_route.extend(path_to_destination[1:])
                current_city = loaded_package.destination
                delivered_ids.append(loaded_package.id)

        full_route = self._remove_consecutive_duplicates(full_route)
        plan = {
            "camion_id": vehicle.id,
            "ronda": 1,
            "ciudad_inicio": vehicle.initial_city,
            "paquetes_entregados": delivered_ids,
            "ruta": full_route,
            "distancia": total_distance,
        }
        return plan, delivered_ids, total_distance, priority_penalty, is_valid

    def _load_consecutive_packages(
        self,
        route: List[int],
        start_index: int,
        pickup_city: str,
        capacity: int,
    ) -> Tuple[List[Package], int]:
        load = []
        used_capacity = 0
        index = start_index

        while index < len(route):
            package = self.packages[route[index]]
            if package.pickup != pickup_city:
                break
            if used_capacity + package.size > capacity:
                break
            load.append(package)
            used_capacity += package.size
            index += 1

        return load, index

    def _distance(self, origin: str, destination: str) -> Optional[float]:
        key = (origin, destination)
        if key not in self.distance_cache:
            self.distance_cache[key] = shortest_path(self.graph, origin, destination)
        return self.distance_cache[key]

    def _route(self, origin: str, destination: str) -> Optional[List[str]]:
        key = (origin, destination)
        if key not in self.route_cache:
            self.route_cache[key] = shortest_path_route(self.graph, origin, destination)
        return self.route_cache[key]

    def _precompute_relevant_paths(self) -> None:
        cities = {
            vehicle.initial_city
            for vehicle in self.vehicles
        } | {
            city
            for package in self.packages.values()
            for city in (package.pickup, package.destination)
        }

        for origin in cities:
            for destination in cities:
                self._distance(origin, destination)
                self._route(origin, destination)

    def _build_compatible_vehicles(self) -> Dict[int, List[int]]:
        compatible = {}
        for package in self.packages.values():
            compatible[package.id] = [
                vehicle.index
                for vehicle in self.vehicles
                if package.size <= vehicle.capacity
            ]
        return compatible

    def _build_child(
        self,
        package_order: List[int],
        preferred_assignments: Dict[int, int],
        fallback_assignments: Dict[int, int],
        rng: random.Random,
    ) -> List[List[int]]:
        routes = [[] for _ in self.vehicles]
        for package_id in package_order:
            if rng.random() < 0.65:
                vehicle_index = preferred_assignments.get(package_id)
            else:
                vehicle_index = fallback_assignments.get(package_id)

            if vehicle_index not in self.compatible_vehicles[package_id]:
                vehicle_index = rng.choice(self.compatible_vehicles[package_id])

            routes[vehicle_index].append(package_id)
        return routes

    def _ordered_crossover(
        self,
        first_parent: List[int],
        second_parent: List[int],
        rng: random.Random,
    ) -> List[int]:
        if len(first_parent) < 2:
            return first_parent[:]

        start, end = sorted(rng.sample(range(len(first_parent)), 2))
        child = [None] * len(first_parent)
        child[start:end] = first_parent[start:end]

        remaining = [package_id for package_id in second_parent if package_id not in child]
        remaining_index = 0
        for index, value in enumerate(child):
            if value is None:
                child[index] = remaining[remaining_index]
                remaining_index += 1

        return child

    def _mutate_swap(self, chromosome: List[List[int]], rng: random.Random) -> None:
        positions = self._positions(chromosome)
        if len(positions) < 2:
            return

        first, second = rng.sample(positions, 2)
        route_a, index_a = first
        route_b, index_b = second
        package_a = chromosome[route_a][index_a]
        package_b = chromosome[route_b][index_b]

        if route_b not in self.compatible_vehicles[package_a]:
            return
        if route_a not in self.compatible_vehicles[package_b]:
            return

        chromosome[route_a][index_a], chromosome[route_b][index_b] = (
            chromosome[route_b][index_b],
            chromosome[route_a][index_a],
        )

    def _mutate_move_between_vehicles(self, chromosome: List[List[int]], rng: random.Random) -> None:
        positions = self._positions(chromosome)
        if not positions:
            return

        source_route, source_index = rng.choice(positions)
        package_id = chromosome[source_route].pop(source_index)
        compatible_routes = self.compatible_vehicles[package_id]
        target_route = rng.choice(compatible_routes)
        target_index = rng.randint(0, len(chromosome[target_route]))
        chromosome[target_route].insert(target_index, package_id)

    def _mutate_reverse_segment(self, chromosome: List[List[int]], rng: random.Random) -> None:
        non_empty_routes = [index for index, route in enumerate(chromosome) if len(route) >= 2]
        if not non_empty_routes:
            return

        route_index = rng.choice(non_empty_routes)
        route = chromosome[route_index]
        start, end = sorted(rng.sample(range(len(route)), 2))
        route[start : end + 1] = reversed(route[start : end + 1])

    def _positions(self, chromosome: List[List[int]]) -> List[Tuple[int, int]]:
        return [
            (route_index, package_index)
            for route_index, route in enumerate(chromosome)
            for package_index, _ in enumerate(route)
        ]

    def _route_assignments(self, chromosome: List[List[int]]) -> Dict[int, int]:
        return {
            package_id: route_index
            for route_index, route in enumerate(chromosome)
            for package_id in route
        }

    def _flatten(self, chromosome: List[List[int]]) -> List[int]:
        return [package_id for route in chromosome for package_id in route]

    def _build_packages(self, paquetes_df: pd.DataFrame) -> Dict[int, Package]:
        packages = {}
        for _, row in paquetes_df.iterrows():
            packages[int(row["id"])] = Package(
                id=int(row["id"]),
                size=int(row["size"]),
                priority=int(row["prioridad"]),
                pickup=str(row["oficina_asignada"]).strip().lower(),
                destination=str(row["destino"]).strip().lower(),
            )
        return packages

    def _build_vehicles(self, vehiculos_df: pd.DataFrame) -> List[Vehicle]:
        vehicles = []
        for index, row in vehiculos_df.reset_index(drop=True).iterrows():
            vehicles.append(
                Vehicle(
                    index=index,
                    id=int(row["id"]),
                    capacity=int(row["size"]),
                    initial_city=str(row["initial"]).strip().lower(),
                )
            )
        return vehicles

    def _remove_consecutive_duplicates(self, route: List[str]) -> List[str]:
        if not route:
            return []

        clean_route = [route[0]]
        for city in route[1:]:
            if city != clean_route[-1]:
                clean_route.append(city)
        return clean_route


def genetic_algorithm(
    problem: ProblemGeneticVRP,
    population_size: int = 80,
    generations: int = 250,
    mutation_prob: float = 0.25,
    seed: int = 42,
):
    problem.validate_inputs()
    rng = random.Random(seed)
    population = [problem.create_chromosome(rng) for _ in range(population_size)]
    elite_size = max(2, population_size // 10)

    for _ in range(generations):
        population = sorted(population, key=problem.fitness, reverse=True)
        next_population = population[:elite_size]
        selection_pool = population[: max(elite_size, population_size // 2)]

        while len(next_population) < population_size:
            parent_a, parent_b = rng.sample(selection_pool, 2)
            child_a, child_b = problem.crossover(parent_a, parent_b, rng)
            next_population.append(problem.mutation(child_a, mutation_prob, rng))
            if len(next_population) < population_size:
                next_population.append(problem.mutation(child_b, mutation_prob, rng))

        population = next_population

    best = max(population, key=problem.fitness)
    plan, total_distance, fitness_cost, is_valid = problem.evaluate(best)
    if not is_valid:
        raise RuntimeError("El algoritmo genetico no encontro un plan valido para todos los paquetes.")

    return GeneticResult(
        best_chromosome=best,
        plan=plan,
        total_distance=total_distance,
        fitness_cost=fitness_cost,
    )
