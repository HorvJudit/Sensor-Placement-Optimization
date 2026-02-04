from sensorplace.utility import generate_graph_from_file, add_sensors_to_node, read_graph_from_file
from sensorplace.visualization import visualize_graph, visualize_pareto_front
from sensorplace.optimization import multi_objective_optimization, print_results, sort_results_by_cost
import networkx as nx

G = nx.DiGraph()
edges = [
    (0, 2), (1, 2), # 0 and 1 flow into 2
    (3, 5), (4, 5), # 3 and 4 flow into 5
    (2, 6), (5, 6), # 2 and 5 flow into 6
    (6, 7)          # 6 flows into 7 (Sink)
]
G.add_edges_from(edges)

# G = generate_graph_from_file("dummy_graph", "Dummy graph")
# G = generate_graph_from_file("dnister_network", "Dnister river network")

results = multi_objective_optimization(G,
                                 population_size=50, 
                                 n_offsprings=20, 
                                 term_criteria='n_gen', 
                                 term_crit_num=50, 
                                 eliminate_duplicates=True,
                                 sensor_cost=1.0,
                                 alpha=0.5)

visualize_pareto_front(results)
print_results(results)

_, sorted_X = sort_results_by_cost(results)

result_index = input("Which result do you want to visualize? Give the number from the list above: ")
if result_index.isdigit():
    result_index = int(result_index)
else:
    raise ValueError("Please enter a valid integer index.")
if result_index < 1 or result_index > len(results.F):
    raise ValueError("Index out of range of results.")

print(sorted_X[result_index-1])

#add_sensors_to_node(G, sorted_X[result_index-1])

visualize_graph(G)