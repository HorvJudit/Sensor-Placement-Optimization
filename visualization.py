import networkx as nx
import matplotlib.pyplot as plt
from config import node_colors

def visualize_random_graph(G: nx.Graph) -> None: 
    pos = {}
    
    layer = {}
    x_counter = {"source": 0, "sink": 0, "junction": 0}

    for node in G.nodes(data=True):
        t = node[1]["type"]
        y = {"source": 2, "sink": 0, "junction": 1}[t]
        x = x_counter[t]
        pos[node[0]] = (x, y)
        x_counter[t] += 1
        layer[node[0]] = t

    colors = []
    for node in G.nodes(data=True):
        if node[1]['type'] == 'source':
            colors.append('#20b0ff')
        elif node[1]['type'] == 'sink':
            colors.append("#CD3939")
        else:
            colors.append('#eda01c')

    nx.draw(G, pos, with_labels=True, node_color=colors, arrows=True)
    plt.title("Graph Visualization")
    plt.show()
    
def visualize_specific_graph(G: nx.Graph) -> None:
    pos = {node: G.nodes[node]['pos'] for node in G.nodes()}
    colors = [node_colors[G.nodes[node]['type']] for node in G.nodes()]
    edge_colors = ['black' if G.nodes[node].get('has_sensor', False) else 'none' for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_color=colors, arrows=True, edgecolors=edge_colors)
    plt.title("Graph Visualization")
    plt.show()