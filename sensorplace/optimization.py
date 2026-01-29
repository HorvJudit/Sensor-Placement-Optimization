from collections import deque, Counter
import networkx as nx

def calculate_total_sensor_cost(sensor_cost: float, sensor_num: int) -> float:
    return sensor_cost * sensor_num

def calculate_observation_quality(G: nx.Graph, sensor_positions: list):
    observed_nodes_num_dict = {}
    
    sensor_nodes = [i for i, bit in enumerate(sensor_positions) if bit == 1]
    if not sensor_nodes:
        return ... #TODO: give the type of the empty return value
    
    # Check how many nodes are observed from each sensor node
    # A node is observes if the node has a descendant with a sensor
    # But it is faster to find the all predecessors of the sensor nodes,
    # and it is easier to traverse the graph in the reversed direction.
    reversed_G = G.reverse(copy=False) # Create a view of the graph with reversed edges
    
    
    
    
    # multi-source BFS from each sensor node
    queue = deque(sensor_nodes)
    
    
    
    
    
    
    
