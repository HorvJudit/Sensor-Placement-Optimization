import pytest
import networkx as nx
from sensorplace import optimization

def test_observed_nodes_1():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [0, 0, 1, 0, 0, 0, 1, 0]  # Sensors at nodes 2 and 6
    
    observed_nodes, unobserved_nodes, sensor_to_nodes = optimization.analyze_graph(G, sensor_positions)
    
    assert observed_nodes == {0, 1, 2, 3, 4, 5, 6}
    assert unobserved_nodes == {7}
    assert sensor_to_nodes == {2: [2, 0, 1], 6: [6, 5, 3, 4]}
    
def test_observed_nodes_2():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [0, 0, 0, 0, 0, 0, 0, 0]  # Sensors at nowhere
    
    observed_nodes, unobserved_nodes, sensor_to_nodes = optimization.analyze_graph(G, sensor_positions)
    
    assert observed_nodes == set()
    assert unobserved_nodes == {0, 1, 2, 3, 4, 5, 6, 7}
    assert sensor_to_nodes == {}