from sensorplace.utility import generate_graph_from_file, add_sensors_to_node, get_sensors_from_result
from sensorplace.visualization import visualize_graph, visualize_pareto_front
from sensorplace.optimization import multi_objective_optimization, print_results
import networkx as nx
from sensorplace.utility import get_result_from_user_input, generate_example_graph
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling

# G = generate_example_graph()

G = generate_graph_from_file("dummy_graph", "Dummy graph")
# G = generate_graph_from_file("dnister_network", "Dnister river network")

results = multi_objective_optimization(G,
                                 population_size=50, 
                                 n_offsprings=20, 
                                 term_criteria='n_gen', 
                                 term_crit_num=50, 
                                 eliminate_duplicates=True,
                                 sensor_cost=1.0,
                                 alpha=0.5,
                                 sampling=BinaryRandomSampling(),
                                 crossover=TwoPointCrossover(),
                                 mutation=BitflipMutation())

visualize_pareto_front(results)
print_results(results)

result = get_result_from_user_input(results)
sensors = get_sensors_from_result(result)

add_sensors_to_node(G, sensors)

visualize_graph(G)