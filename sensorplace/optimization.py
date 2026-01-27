import networkx as nx

def calculate_total_sensor_cost(sensor_cost: float, sensor_num: int) -> float:
    return sensor_cost * sensor_num

def calculate_observation_quality(G: nx.Graph, sensor_positions: list, is_system_open: float) -> float:
    ...
    
def calculate_observed_nodes_by_one_sensor(G: nx.Graph, sensor_positions: list, is_system_open: float) -> float:
    ...
    
def calculate_unobserved_nodes(G: nx.Graph, sensor_positions: list, is_system_open: float) -> float:
    ...