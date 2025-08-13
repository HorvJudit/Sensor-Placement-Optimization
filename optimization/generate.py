import networkx as nx
import numpy as np
import random

def generate_population(G: nx.Graph, population_size: int, chance_of_sensor: int = 0.5) -> list:
    population = []
    for _ in range(population_size):
        individual = generate_individual(G, chance_of_sensor)
        population.append(individual)
    return population

def generate_individual(G: nx.Graph, chance_of_sensor:int) -> dict:
    individual = {}
    genome = np.zeros(G.number_of_nodes(), dtype=bool)
    for i in range(len(genome)):
        genome[i] = random.random() < chance_of_sensor
    
    individual['genome'] = genome
    return individual