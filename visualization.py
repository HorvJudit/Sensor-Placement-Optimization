import os
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import random
from networkx.drawing.nx_agraph import graphviz_layout
from config import node_colors
import tkinter as tk

def calculate_graph_layout(G:nx.Graph, min_h_distance: int = 1.5, min_v_distance: int = 2.0, iterations: int = 10) -> dict[int, tuple[int, int]]:
    """Calculates the (x, y) positions for each node in the graph G using a simple layout algorithm."""
    
    adjacency, reversed_adjacency = _build_graph_structure(G)
    max_layer, nodes_by_layer = _assign_layers(G, reversed_adjacency)
    positions = _initialize_positions(nodes_by_layer, max_layer, min_h_distance, min_v_distance)
    _optimize_node_order(nodes_by_layer, adjacency, reversed_adjacency, positions, min_h_distance, max_layer, iterations)
    final_coordinates = _finalize_coordinates(nodes_by_layer, positions, min_h_distance, max_layer)
    return final_coordinates
    
    
def _build_graph_structure(G: nx.Graph) -> tuple[dict, dict]:
    """Builds adjacency lists from edge list."""
    adj = {}
    reversed_adj = {} # parents
    
    for u, v in G.edges():
        if u not in adj:
            adj[u] = []
        adj[u].append(v)
        if v not in reversed_adj:
            reversed_adj[v] = []
        reversed_adj[v].append(u)
        
    for node in G.nodes():
        if node not in adj:
            adj[node] = []
        if node not in reversed_adj:
            reversed_adj[node] = []   
             
    return adj, reversed_adj

def _assign_layers(G: nx.Graph, reversed_adjacency) -> tuple[int, dict, dict]:
    """Calculates the layer (depth) for each node using DFS/Memoization."""
    memo = {}
    
    def get_depth(node, path_stack):
        if node in memo:
            return memo[node]        
        if node in path_stack:
            return 0  # Prevent cycles    
        
        parents = reversed_adjacency[node]
        if not parents:
            return 0
        
        path_stack.append(node)
        max_parent_depth = 0
        for parent in parents:
            parent_depth = get_depth(parent, path_stack)
            if parent_depth > max_parent_depth:
                max_parent_depth = parent_depth
        path_stack.pop()
        
        depth = max_parent_depth + 1
        memo[node] = depth
        return depth
    
    nodes_by_layer = {}
    max_layer = 0
    
    for node in G.nodes:
        layer_index = get_depth(node, [])        
        if layer_index not in nodes_by_layer:
            nodes_by_layer[layer_index] = []
        nodes_by_layer[layer_index].append(node)
        if layer_index > max_layer:
            max_layer = layer_index
            
    return max_layer, nodes_by_layer

def _initialize_positions(nodes_by_layer, max_layer, min_h_distance, min_v_distance):
    """Sets initial X, Y positions based on arbitrary order."""
    positions = {}
    for layer_index in range(max_layer + 1):
        if layer_index in nodes_by_layer:
            layer_nodes = nodes_by_layer[layer_index]
            for i, node in enumerate(layer_nodes):
                positions[node] = {
                    'x': i * min_h_distance, 
                    'y': -layer_index * min_v_distance
                }  # Initial x based on index, y based on layer
    return positions
        
def _optimize_node_order(nodes_by_layer, adjacency, reversed_adjacency, positions, min_h_distance, max_layer, iterations):
    """Modifies 'positions' and 'nodes_by_layer' in-place using Barycenter heuristic."""
    for _ in range(iterations):
        # Down sweep
        for layer_index in range(1, max_layer + 1):
            _apply_barycenter_sort(layer_index, nodes_by_layer, reversed_adjacency, positions, min_h_distance)
        # Up sweep
        for layer_index in range(max_layer - 1, -1, -1):
            _apply_barycenter_sort(layer_index, nodes_by_layer, adjacency, positions, min_h_distance) 
    
def _apply_barycenter_sort(layer_index, nodes_by_layer, neighbors_adjacency, positions, min_h_distance):
    """Sorts a single layer based on average position of neighbors."""
    if layer_index not in nodes_by_layer:
        return
    
    current_nodes = nodes_by_layer[layer_index]
    new_order = []
    
    for node in current_nodes:
        neighbors = neighbors_adjacency[node]
        if not neighbors:
            # Keep current X if no neighbors constrain it
            new_order.append((positions[node]['x'], node))
            continue
        
        # Calculate average X of neighbors
        average_x = sum(positions[neighbor]['x'] for neighbor in neighbors) / len(neighbors)
        new_order.append((average_x, node))
        
    # Sort nodes based on average neighbor X
    new_order.sort(key=lambda x: x[0])
    
    # Reassing strictly spaced X coordinates based on the new order
    # (This prevents nodes from collapsing into the same position)
    for i, (average_x, node) in enumerate(new_order):
        positions[node]['x'] = i * min_h_distance
        
    # update the layer list with the new order
    nodes_by_layer[layer_index] = [node for _, node in new_order] 
    
def _finalize_coordinates(nodes_by_layer, positions, min_h_distance, max_layer):
    """Centers the layers and returns the final plain coordinate dictionary."""
    final_coordinates = {}
    max_width = 0
    
    # 1. Determine the width of each layer and find the widest one
    layer_widths = {}
    for layer_index in range(max_layer + 1):
        if layer_index not in nodes_by_layer:
            continue
        
        layer_nodes = nodes_by_layer[layer_index]
        width = (len(layer_nodes) - 1) * min_h_distance
        layer_widths[layer_index] = width
        if width > max_width:
            max_width = width
    
    # 2. Assign final coordinates with centering offset
    for layer_index in range(max_layer + 1):
        if layer_index not in nodes_by_layer:
            continue
        
        layer_nodes = nodes_by_layer[layer_index]
        current_width = layer_widths[layer_index]
        offset = (max_width - current_width) / 2
        
        # We use the sorted order from nodes_by_layer
        for i, node in enumerate(layer_nodes):
            x = (i * min_h_distance) + offset
            y = positions[node]['y'] # already correct
            final_coordinates[node] = (x, y)
            
    return final_coordinates


def visualize_graph(G: nx.Graph, title: str = None, save: bool = False) -> None:
    
    coordinates = calculate_graph_layout(G)

    # makes the figure size fullscreen (there will be no margins)
    plt.figure(figsize=_get_fig_size_from_screen())
    pos = {node: coordinates[node] for node in G.nodes()}
    
    colors = [node_colors['sensor'] if G.nodes[node].get('has_sensor', False) else node_colors['default'] for node in G.nodes()]            
    weights = nx.get_edge_attributes(G, 'weight')
            
    nx.draw(G, pos, with_labels=True, node_color=colors, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
    if title:
        plt.title(title)
    plt.show()
    
    # if save:
    #     folder = "graph_images"
        
    #     if title:
    #         filename = title.replace(" ", "_") + ".png"
    #     else:
    #         filename = "graph.png"
    #     file_path = os.path.join(folder, filename)
    #     plt.savefig(file_path) # it saves a blank canvas, not working
    #     print(f"Graph saved as {filename}")


def _get_fig_size_from_screen() -> tuple:
    # screen resolution
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    # get DPI
    dpi = matplotlib.rcParams['figure.dpi']
    # calculate figure size in inches
    fig_width = screen_width / dpi
    fig_height = screen_height / dpi
    
    return fig_width, fig_height