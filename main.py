from utility import generate_graph_from_file, generate_random_graph, add_sensors_to_node, read_graph_from_file
from visualization import visualize_graph
#from optimization.generate import generate_population
import networkx as nx

#G = generate_random_graph(seed = 45, nodes_num = 20, source_nodes_num = 3, sink_nodes_num = 2)
G = generate_graph_from_file("test_network1")
# sensor_nodes = [1, 2, 3, 4, 5, 20, 21, 22]
# add_sensors_to_node(G, sensor_nodes)
print(G.nodes(data=True))
visualize_graph(G)

# population = generate_population(G, population_size=10, chance_of_sensor=0.7)
# individual = population[0]