from collections import deque, Counter
import networkx as nx

import numpy as np
import math
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.optimize import minimize

def calculate_cost(sensor_positions: list, sensor_cost: float = 1.0) -> float:
    """
    Calculate the total cost of deployed sensors. 
    """
    sensor_num = sensor_positions.count(1)
    return sensor_cost * sensor_num

def calculate_observation_quality(G: nx.Graph, sensor_positions: list, alpha=0.5) -> float:
    """
    Calculate the observation quality based on sensor positions.
    Observation quality is calculated by considering the load on each sensor and the number of observed nodes.
    Parameters:
    G : nx.Graph
        The directed graph representing the network.
    sensor_positions : list
        A binary list indicating the positions of sensors in the graph (1 for sensor, 0 for no sensor).
    alpha : float
        The load balancing exponent. Higher values penalize sensors with higher loads more.
        if alpha = 0.1, that means more weight on observing more nodes,
        if alpha = 0.5, balance between observing more nodes and load balancing and high resolution,
        if alpha = 0.9, more weight on load balancing and high resolution.
        Keep alpha between 0.1 and 0.9 for reasonable results.
    Returns:
    float
        The calculated observation quality.        
    """
    _, _, sensor_to_nodes = analyze_graph(G, sensor_positions)
    
    total_score = 0.0
    
    for sensor, nodes in sensor_to_nodes.items():
        load = len(nodes)
        
        if load > 0:
            node_score = 1.0 / (load ** alpha)
            
            sensor_contribution = node_score * load
            total_score += sensor_contribution
            
    return total_score
    

def analyze_graph(G: nx.Graph, sensor_positions: list) -> tuple[set, set, dict]:
    
    sensor_nodes = [i for i, bit in enumerate(sensor_positions) if bit == 1]
    if not sensor_nodes:
        return set(), set(G.nodes()), {}
    # Check how many nodes are observed from each sensor node
    # A node is observes if the node has a descendant with a sensor
    # But it is faster to find the all predecessors of the sensor nodes,
    # and it is easier to traverse the graph in the reversed direction.
    reversed_G = G.reverse(copy=False) # Create a view of the graph with reversed edges
    
    # sensor_to_nodes maps each sensor node to the set of nodes it can observe
    # initially we add each sensor node, because each sensor observes their sensor node
    sensor_to_nodes = {sensor_node: [sensor_node] for sensor_node in sensor_nodes}
    # print(sensor_to_nodes) # DEBUG
    
    # node_to_sensor_position maps each node to the closest sensor node that observes it
    # initially we can add just the sensor position nodes
    node_to_sensor_position = {sensor_node: sensor_node for sensor_node in sensor_nodes}
    # print(node_to_sensor_position) # DEBUG
    
    # multi-source BFS from each sensor node
    queue = deque(sensor_nodes)
    
    while queue:
        current_node = queue.popleft()
        observer_sensor_position = node_to_sensor_position[current_node]
        
        for upstream_neighbor in reversed_G.neighbors(current_node):
            # If the neighbor hasn't belonged to any sensor yet
            if upstream_neighbor not in node_to_sensor_position:
                # Claim it for the current sensor
                node_to_sensor_position[upstream_neighbor] = observer_sensor_position
                sensor_to_nodes[observer_sensor_position].append(upstream_neighbor)
                queue.append(upstream_neighbor)
        
    # print(sensor_to_nodes) # DEBUG    
    observed_nodes = set(node_to_sensor_position.keys())    
    unobserved_nodes = set(G.nodes()) - observed_nodes
    
    
    return observed_nodes, unobserved_nodes, sensor_to_nodes

class SensorPlacementProblem(ElementwiseProblem):
    def __init__(self, G: nx.DiGraph, alpha: float = 0.5, sensor_cost: float = 1.0):
        self.G = G
        self.sensor_cost = sensor_cost
        self.alpha = alpha
        
        # Define the problem characteristics
        # n_var: Number of variables (number of potential sensor locations)
        # n_obj: Number of objectives (2: Cost and Quality)
        # n_ieq_constr: Number of constraints (0 for now)
        super().__init__(n_var=G.number_of_nodes(), 
                         n_obj=2, 
                         n_ieq_constr=0, 
                         xl=0, xu=1) # Binary variables (0 or 1)

    def _evaluate(self, x, out, *args, **kwargs):
        """
        Evaluation function for a SINGLE solution (individual).
        x: A binary array (e.g., [0, 1, 0, 1...]) indicating active sensors.
        """
        sensor_positions = x.tolist()
        
        total_cost = calculate_cost(sensor_positions, self.sensor_cost)
        observation_quality = calculate_observation_quality(self.G, sensor_positions, self.alpha)
        
        # We want to minimize cost and maximize observation quality
        out["F"] = [total_cost, -observation_quality]
        
def multi_objective_optimization(G: nx.DiGraph, population_size: int, n_offsprings: int, term_criteria: str, term_crit_num: int, eliminate_duplicates: bool, sensor_cost: float = 1.0, alpha: float = 0.5): 
    """
    Perform multi-objective optimization for sensor placement using NSGA-II.
    Parameters:
    G : nx.DiGraph
        The directed graph representing the network.
    population_size : int
        The size of the population in the genetic algorithm.
    n_offsprings : int
        The number of offsprings to produce in each generation. The differene between population_size and n_offsprings is the number of elites.
    term_criteria : str
        The termination criteria for the optimization ('n_gen' for number of generations).
    term_crit_num : int
        The number associated with the termination criteria (e.g., number of generations).
    eliminate_duplicates : bool
        Whether to eliminate duplicate solutions in the population.
    sensor_cost : float
        The cost associated with deploying a single sensor.
    alpha : float
        The load balancing exponent. Higher values penalize sensors with higher loads more.
        if alpha = 0.1, that means more weight on observing more nodes,
        if alpha = 0.5, balance between observing more nodes and load balancing and high resolution,
        if alpha = 0.9, more weight on load balancing and high resolution.
        Keep alpha between 0.1 and 0.9 for reasonable results.
    Returns:
    res : pymoo.core.result.Result
        The result object containing the optimization results.
    """
    problem = SensorPlacementProblem(G, alpha, sensor_cost)

    # Setup the NSGA-II algorithm
    algorithm = NSGA2(
        pop_size=population_size,
        n_offsprings=n_offsprings,
        sampling=BinaryRandomSampling(),
        crossover=TwoPointCrossover(),
        mutation=BitflipMutation(),
        eliminate_duplicates=eliminate_duplicates
    )
    
    print("Running optimization...")

    # Run the optimization
    results = minimize(problem,
                   algorithm,
                   (term_criteria, term_crit_num),
                   # seed=42,
                   verbose=True)
    
    return results

def sort_results_by_cost(results):
    # Sort results by cost (first objective)
    sorted_indices = np.argsort(results.F[:, 0])
    sorted_F = results.F[sorted_indices]
    sorted_X = results.X[sorted_indices]
    
    return sorted_F, sorted_X

def print_results(results):
    sorted_F, sorted_X = sort_results_by_cost(results)

    for i in range(len(sorted_F)):
        cost = sorted_F[i, 0]
        quality = -1 * sorted_F[i, 1] # Convert back to positive
        
        # Get active sensors for this solution
        active_sensors = np.where(sorted_X[i] == 1)[0].tolist()
        
        print(f"Solution {i+1}: Cost={cost:.1f} | Quality={quality:.4f} | Sensors at: {active_sensors}")
    
    
if __name__ == "__main__":
    # Create a simple test graph (Directed tree-like structure)
    # 7 -> 6 -> 5 -> 3, 4
    # 2 -> 0, 1
    # Connected components merging at 2 and 6
    G = nx.DiGraph()
    edges = [
        (0, 2), (1, 2), # 0 and 1 flow into 2
        (3, 5), (4, 5), # 3 and 4 flow into 5
        (2, 6), (5, 6), # 2 and 5 flow into 6
        (6, 7)          # 6 flows into 7 (Sink)
    ]
    G.add_edges_from(edges)
    
    print(f"Graph created with {G.number_of_nodes()} nodes.")

    results = multi_objective_optimization(G, 
                               population_size=50, 
                               n_offsprings=20, 
                               term_criteria='n_gen', 
                               term_crit_num=50, 
                               eliminate_duplicates=True,
                               sensor_cost=1.0,
                               alpha=0.5)

    print_results(results)
    
    
    
    
