import networkx as nx
import pickle
import numpy as np
import pandas as pd

from sensorplace.optimization import sort_results_by_cost

def parameter_validation(nodes_num, source_nodes_num, sink_nodes_num):
    if nodes_num is not None:
        if nodes_num < 1:
            raise ValueError("Number of nodes must be at least 1.")
        if source_nodes_num is not None and source_nodes_num >= nodes_num:
            raise ValueError("Number of source nodes must be less than total number of nodes.")
        if sink_nodes_num is not None and sink_nodes_num >= nodes_num:
            raise ValueError("Number of sink nodes must be less than total number of nodes.")
        if source_nodes_num is not None and sink_nodes_num is not None and source_nodes_num + sink_nodes_num >= nodes_num:
            raise ValueError("Sum of source and sink nodes must be less than total number of nodes.")
        
def get_destination_file_path(graph_name: str, folder_name = "predefined graphs") -> str:
    import os
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = graph_name + ".pkl"  
    file_path = os.path.join(folder_name, filename)
    return file_path

def generate_graph_from_file(graph_name: str, folder_name: str) -> nx.Graph:
    
    import os    
    dataset_file_path = os.path.join("datasets", folder_name, "data.xlsx")   
    
    if graph_name is not None and os.path.exists(graph_name):
        # Check if the graph file exists        
        return read_graph_from_file(graph_name)
    else:    
        G = build_graph_from_excel_file(dataset_file_path)
        write_graph_to_file(G, graph_name)
        return G

def build_graph_from_excel_file(file_path: str) -> nx.Graph:
    
    df = pd.read_excel(file_path)
    return build_graph_from_dataframe(df)

def build_graph_from_dataframe(df: pd.DataFrame) -> nx.Graph:
    G = nx.from_pandas_edgelist(df, source='from', target='to', edge_attr='weight', create_using=nx.DiGraph)
    nx.set_node_attributes(G, False, name='has_sensor')    
    node_categorizer(G)

    return G


def node_categorizer(G: nx.DiGraph) -> None :
    for node in G.nodes():
        if G.out_degree(node) == 0:
            G.nodes[node]['type'] = 'sink'
        elif G.in_degree(node) == 0:
            G.nodes[node]['type'] = 'source'
        else:
            G.nodes[node]['type'] = 'junction'

def read_graph_from_file(graph_name: str) -> nx.Graph:
    file_path = get_destination_file_path(graph_name)
    with open(file_path, "rb") as f:
        G = pickle.load(f)
    return G

def write_graph_to_file(G: nx.Graph, graph_name: str) -> None:
    file_path = get_destination_file_path(graph_name)
    with open(file_path, "wb") as f:
        pickle.dump(G, f)
        
def add_sensors_to_node(G: nx.Graph, node_id_list: list[int]) -> None:
    for node_id in node_id_list:
        if node_id not in G.nodes:
            raise ValueError(f"Node {node_id} does not exist in the graph.")
        G.nodes[node_id]['has_sensor'] = True
        
def get_result_from_user_input(results):
    _, sorted_X = sort_results_by_cost(results)
    
    result_index = input("Which result do you want to visualize? Give the number from the list above: ")
    if result_index.isdigit():
        result_index = int(result_index)
    else:
        raise ValueError("Please enter a valid integer index.")
    if result_index < 1 or result_index > len(results.F):
        raise ValueError("Index out of range of results.")
    
    result = sorted_X[result_index-1]
    
    return result
    

def get_sensors_from_result(result) -> list[int]:
    active_sensors = np.where(result == 1)[0].tolist()
    return active_sensors

def generate_example_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    edges = [
        (0, 2), (1, 2), # 0 and 1 flow into 2
        (3, 5), (4, 5), # 3 and 4 flow into 5
        (2, 6), (5, 6), # 2 and 5 flow into 6
        (6, 7)          # 6 flows into 7 (Sink)
    ]
    G.add_edges_from(edges)
    node_categorizer(G)
    return G