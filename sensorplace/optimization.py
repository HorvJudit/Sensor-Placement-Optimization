import networkx as nx

def calculate_total_sensor_cost(sensor_cost: float, sensor_num: int) -> float:
    return sensor_cost * sensor_num

def calculate_observation_quality(G: nx.Graph, sensor_positions: list):
    observed_nodes_num_dict = {}
    
    sensor_nodes = [i for i, bit in enumerate(sensor_positions) if bit == 1]
    if not sensor_nodes:
        return ... #TODO: give the type of the empty return value
    
    
    
    
    
    
    
