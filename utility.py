import networkx as nx
import pickle
import random

def generate_random_graph(seed: int = None, nodes_num:int = None, source_nodes_num:int = None, sink_nodes_num:int = None) -> nx.Graph:

    parameter_validation(nodes_num, source_nodes_num, sink_nodes_num)
    
    if seed is not None:
        random.seed(seed)
        
    if nodes_num is None:
        nodes_num = random.randint(5, 20)        
    if source_nodes_num is None:
        source_nodes_num = random.randint(1, nodes_num // 2)
    if sink_nodes_num is None:
        sink_nodes_num = random.randint(1, nodes_num // 2)
        
    G = nx.DiGraph()
    
    # Add nodes
    nodes = list(range(nodes_num))
    random.shuffle(nodes)
    
    source_nodes = nodes[:source_nodes_num]
    sink_nodes = nodes[source_nodes_num:source_nodes_num + sink_nodes_num]
    junction_nodes = nodes[source_nodes_num + sink_nodes_num:]
    
    for node in source_nodes:
        G.add_node(node, type="source", has_sensor=False)

    for node in sink_nodes:
        G.add_node(node, type="sink", has_sensor=False)

    for node in junction_nodes:
        G.add_node(node, type="junction", has_sensor=False)
        
    # Add edges
    for i_node in nodes:
        for j_node in nodes:
            if i_node == j_node:
                continue
            if i_node not in sink_nodes and j_node not in source_nodes:
                if random.random() < 0.05:
                    G.add_edge(i_node, j_node)
            if j_node not in sink_nodes and i_node not in source_nodes:
                if random.random() < 0.05:
                    G.add_edge(j_node, i_node)
    
    return G

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
        

def generate_graph_from_file(graphname: str) -> nx.Graph:
    import os
    folder = "predefined graphs"
    filename = graphname + ".pkl"   
    file_path = os.path.join(folder, filename)
    
    if graphname is not None and os.path.exists(file_path):
        # Check if the graph file exists        
        return read_graph_from_file(file_path)
    else:    
        excel_file_path = "graph_data.xlsx"    
        G = build_graph(excel_file_path, graphname)
        write_graph_to_file(G, file_path)
        return G

def build_graph(file_path: str, graphname: str) -> nx.Graph:
    import pandas as pd
    df_nodes = pd.read_excel(file_path, sheet_name=graphname+'_nodes')
    df_edges = pd.read_excel(file_path, sheet_name=graphname+'_edges')
    G = nx.DiGraph()
    
    # Add nodes
    from config import node_types
    for index, row in df_nodes.iterrows():
        if row['type'] not in node_types:
            raise ValueError(f"Invalid node type: {row['type']}")
        G.add_node(row['node_id'], type=row['type'], has_sensor=False, pos=(row['x'], row['y']))

    # Add edges
    sink_nodes = [node for node, data in G.nodes(data=True) if data.get('type') == 'sink']
    source_nodes = [node for node, data in G.nodes(data=True) if data.get('type') == 'source']
    
    for index, row in df_edges.iterrows():
        if row['from'] not in G.nodes or row['to'] not in G.nodes:
            raise ValueError(f"Edge from {row['from']} to {row['to']} contains invalid nodes.")
        if row['from'] == row['to']:
            raise ValueError("Self-loops are not allowed.")
        if row['from'] in sink_nodes:
            raise ValueError(f"Cannot add edge from sink node {row['from']}.")
        if row['to'] in source_nodes:
            raise ValueError(f"Cannot add edge to source node {row['to']}.")
                
        G.add_edge(row['from'], row['to'], weight=row['weight'])

    return G


def read_graph_from_file(file_path: str) -> nx.Graph:
    with open(file_path, "rb") as f:
        G = pickle.load(f)
    return G

def write_graph_to_file(G: nx.Graph, file_path: str) -> None:
    with open(file_path, "wb") as f:
        pickle.dump(G, f)
        
def add_sensors_to_node(G: nx.Graph, node_id_list: list[int]) -> None:
    for node_id in node_id_list:
        if node_id not in G.nodes:
            raise ValueError(f"Node {node_id} does not exist in the graph.")
        G.nodes[node_id]['has_sensor'] = True