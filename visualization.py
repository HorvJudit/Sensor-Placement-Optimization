import networkx as nx
import matplotlib.pyplot as plt
from config import node_colors

def visualize_graph(G: nx.Graph) -> None:
    pos = {node: G.nodes[node]['pos'] for node in G.nodes()}
    
    colors = []    
    for node in G.nodes():
        if G.nodes[node].get('has_sensor', False):
            colors.append(node_colors['sensor'])
        else:
            colors.append(node_colors['default'])
            
    nx.draw(G, pos, with_labels=True, node_color=colors, arrows=True)
    plt.show()