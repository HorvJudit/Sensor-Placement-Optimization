import pytest
import networkx as nx
from sensorplace import optimization

def test_observation_quality_1():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [1, 1, 1, 1, 1, 1, 0, 0]    
    observation_quality = optimization.calculate_observation_quality(G, sensor_positions)
    
    assert observation_quality == 6.0
    
def test_observation_quality_2():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [0, 0, 1, 0, 0, 1, 0, 0]    
    observation_quality = optimization.calculate_observation_quality(G, sensor_positions)
    
    assert round(observation_quality, 2) == 3.46
    
def test_observation_quality_3():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [1, 0, 0, 0, 0, 0, 0, 0]    
    observation_quality = optimization.calculate_observation_quality(G, sensor_positions)
    
    assert observation_quality == 1.0
    
def test_observation_quality_4():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [0, 0, 0, 0, 0, 0, 0, 1]    
    observation_quality = optimization.calculate_observation_quality(G, sensor_positions)
    
    assert round(observation_quality, 2) == 2.83
    
def test_observation_quality_5():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [0, 0, 1, 0, 0, 0, 1, 0]    
    observation_quality = optimization.calculate_observation_quality(G, sensor_positions)
    
    assert round(observation_quality, 2) == 3.73
    
def test_observation_quality_6():
    G = nx.DiGraph()
    G.add_edges_from([(0,2), (1,2), (3, 5), (4,5), (2,6), (5,6), (6,7)])
    sensor_positions = [1, 0, 0, 0, 0, 0, 1, 0]    
    observation_quality = optimization.calculate_observation_quality(G, sensor_positions)
    
    assert round(observation_quality, 2) == 3.45