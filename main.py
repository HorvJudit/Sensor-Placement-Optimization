from sensorplace.utility import generate_graph_from_file, add_sensors_to_node, read_graph_from_file
from sensorplace.visualization import visualize_graph
#from optimization.generate import generate_population
import networkx as nx

G = generate_graph_from_file("dnister_network", "Dnister river network")
# G = read_graph_from_file("dnister_network")
print(list(G.nodes(data=True))[0])
#G = generate_graph_from_file("dummy_graph", "Dummy graph")
#G = ...

# sensor_nodes = [1, 2, 3, 4, 5, 20, 21, 22]
# add_sensors_to_node(G, sensor_nodes)
visualize_graph(G)
print(list(G.nodes(data=True))[0])

# population = generate_population(G, population_size=10, chance_of_sensor=0.7)
# individual = population[0]