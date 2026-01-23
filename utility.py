import networkx as nx
import pickle

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
        

def generate_graph_from_file(graphname: str, excel_file_path: str) -> nx.Graph:
    import os
    folder = "predefined graphs"
    filename = graphname + ".pkl"   
    file_path = os.path.join(folder, filename)
    
    if graphname is not None and os.path.exists(file_path):
        # Check if the graph file exists        
        return read_graph_from_file(file_path)
    else:    
        G = build_graph(excel_file_path)
        write_graph_to_file(G, file_path)
        return G

def build_graph(file_path: str) -> nx.Graph:
    import pandas as pd
    df_nodes = pd.read_excel(file_path, sheet_name='nodes')
    df_edges = pd.read_excel(file_path, sheet_name='edges')
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