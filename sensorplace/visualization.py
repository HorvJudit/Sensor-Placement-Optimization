import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from sensorplace.config import node_colors
import tkinter as tk

def calculate_graph_layout(G: nx.Graph, min_h_distance: int = 1, min_v_distance: int = -5) -> dict:
    longest_path_in_graph = nx.dag_longest_path(G, weight=None)
    longest_path_map = _calculate_longest_path_map(G)
    coordinates = _positions(G, longest_path_in_graph, longest_path_map, min_v_distance, min_h_distance)
    return coordinates
    
def _calculate_longest_path_map(G: nx.Graph) -> dict:
    """Generate a mapping of nodes to their longest path lengths from source nodes."""
    longest_path_map = {}
    
    for node in nx.topological_sort(G):
        parents = list(G.predecessors(node))
        if not parents:
            # If no parents, path length is 0 (it's a root)
            longest_path_map[node] = 0
        else:
            # Max length is 1 + maximum length of any parent
            parent_lengths = [longest_path_map[p] for p in parents]
            longest_path_map[node] = 1 + max(parent_lengths)

    return longest_path_map

def _positions(G: nx.Graph, longest_path_in_graph: list, longest_path_map: dict, min_v_distance: int, min_h_distance: int) -> dict:
    coordinates = {}
    occupied_positions = set()

    for i, node in enumerate(longest_path_in_graph):
        # --- 1. Place the Backbone Node ---
        if i == 0:
            coordinate = (0, 0)
        else:
            path_parent = longest_path_in_graph[i - 1]
            parent_x, parent_y = coordinates[path_parent]
            coordinate = (0, parent_y + min_v_distance) # Backbone is centered at X=0
            
        coordinates[node] = coordinate
        occupied_positions.add(coordinate)

        # --- 2. Process Ancestors (Iteratively) ---
        # We use a queue to process parents, grandparents, etc.
        # We start with the current backbone node to find its side-parents
        nodes_to_process = [node]
        
        while nodes_to_process:
            current_child = nodes_to_process.pop(0)
            child_x, child_y = coordinates[current_child]
            
            # Find parents that are NOT placed yet
            # (This automatically excludes backbone nodes placed in previous/future steps)
            unplaced_parents = [
                p for p in G.predecessors(current_child) 
                if p not in coordinates
            ]
            
            # Sort by depth map to keep layout consistent
            unplaced_parents = sorted(unplaced_parents, key=lambda p: longest_path_map.get(p, 0))
            
            for j, parent in enumerate(unplaced_parents):
                # Logic: Parents are placed one level "above" the child (-Y direction)
                # Note: In your original code, side-parents were at same level as backbone parent.
                # Mathematically: parent_y = child_y - min_v_distance
                target_y = child_y - min_v_distance
                
                # Start X search slightly to the right of the child (or keep branching out)
                # To make it look nice, we try to place it relative to the child's X
                initial_offset = (j + 1) * min_h_distance
                candidate_x = child_x + initial_offset
                
                # Collision detection
                # We round coordinates to avoid float precision errors
                while (round(candidate_x, 2), round(target_y, 2)) in occupied_positions:
                    candidate_x += min_h_distance
                
                # Save position
                coordinates[parent] = (candidate_x, target_y)
                occupied_positions.add((round(candidate_x, 2), round(target_y, 2)))
                
                # CRITICAL STEP: Add this parent to the queue so ITS parents get processed too
                nodes_to_process.append(parent)

    return coordinates      

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

def visualize_pareto_front(results) -> None:
    """
    Visualizes the Pareto Front from the pymoo result object.
    """
    # 1. Extract the objective values
    # F[:, 0] is Cost (x-axis)
    # F[:, 1] is Negative Quality (y-axis needs flipping)
    costs = results.F[:, 0]
    qualities = -1 * results.F[:, 1]  # Flip back to positive!

    # 2. Setup the plot
    plt.figure(figsize=(10, 6))
    
    # Scatter plot
    plt.scatter(costs, qualities, s=80, c='red', edgecolors='black', label='Pareto Optimal Solutions')
    
    # 3. Aesthetics
    plt.title('Pareto Front: Cost vs. Observation Quality', fontsize=14)
    plt.xlabel('Sensor Cost', fontsize=12)
    plt.ylabel('Observation Quality', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 4. Annotate points (Optional but helpful)
    # This helps you see exactly which point corresponds to which cost
    for i, txt in enumerate(costs):
        # Only label some points to avoid clutter if you have many
        plt.annotate(f"{int(txt)}", (costs[i], qualities[i]), xytext=(5, 5), textcoords='offset points', fontsize=8)

    plt.legend()
    plt.show()