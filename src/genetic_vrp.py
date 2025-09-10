import random
from typing import List, Dict, Tuple, Sequence, Optional
from src.graph_utils import shortest_path

class ProblemGeneticVRP:
    def __init__(self, paquetes_df, ciudad_inicial, grafo):
        self.genes = list(paquetes_df['destino'].str.lower().unique()) 
        self.ciudades = self.genes 
        self.initial = ciudad_inicial.lower()
        self.graph = grafo

    def decode(self, chromosome):
        return chromosome

    def fitness(self, chromosome):
        total_distance = 0
        actual = self.initial
        visited = set()
        penalty = 0
    
        for city in chromosome:
            if city in visited:
                penalty += 1000  # penaliza repetir ciudades
            visited.add(city)
            
            d = shortest_path(self.graph, actual, city)
            if d is None:
                return -999999  # penaliza por camino inválido
            total_distance += d
            actual = city

        penalty += int(0.1 * total_distance)
    
        return -(total_distance + penalty)

    def mutation(self, c, prob):
        c = list(c)
        for i in range(len(c)):
            if random.random() < prob:
                j = random.randint(0, len(c)-1)
                c[i], c[j] = c[j], c[i]
        return c

    def crossover(self, c1, c2):
        if len(c1) < 3:
            return [c1[:], c2[:]]
        pos = random.randint(1, len(c1) - 2)
        cr1 = c1[:pos] + [g for g in c2 if g not in c1[:pos]]
        cr2 = c2[:pos] + [g for g in c1 if g not in c2[:pos]]
        return [cr1, cr2]
    
def genetic_algorithm(problem, population_size=20, generations=100, mutation_prob=0.1):
    if len(problem.ciudades) < 2:
        return problem.ciudades, 0 

    poblacion = [random.sample(problem.ciudades, len(problem.ciudades)) for _ in range(population_size)]

    for _ in range(generations):
        poblacion = sorted(poblacion, key=problem.fitness, reverse=True)
        nueva_pob = poblacion[:2]

        while len(nueva_pob) < population_size:
            p1, p2 = random.choices(poblacion[:10], k=2)
            for hijo in problem.crossover(p1, p2):
                nueva_pob.append(problem.mutation(hijo, mutation_prob))

        poblacion = nueva_pob

    mejor = max(poblacion, key=problem.fitness)
    return mejor, -problem.fitness(mejor)