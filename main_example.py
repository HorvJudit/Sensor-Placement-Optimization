from sensorplace.utility import generate_example_graph
from sensorplace.optimization import multi_objective_optimization
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling

G = generate_example_graph()
results = multi_objective_optimization(G,
                                 population_size=50, 
                                 n_offsprings=20, 
                                 term_criteria='n_gen', 
                                 term_crit_num=50, 
                                 eliminate_duplicates=True,
                                 sampling=BinaryRandomSampling(),
                                 crossover=TwoPointCrossover(),
                                 mutation=BitflipMutation(),
                                 sensor_cost=1.0,
                                 alpha=0.5)

                                    

