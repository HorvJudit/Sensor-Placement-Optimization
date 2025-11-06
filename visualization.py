import os
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from config import node_colors
import tkinter as tk

def visualize_graph(G: nx.Graph, title: str = None, save: bool = False, spring: bool = False) -> None:

    # makes the figure size fullscreen (there will be no margins)
    plt.figure(figsize=get_fig_size_from_screen())

    if spring:
        pos = nx.spring_layout(G)
    #pos = {node: G.nodes[node]['pos'] for node in G.nodes()}    # for the test network, not the real Greenland data
    pos = nx.multipartite_layout(G, subset_key="layer")        
    
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


def get_fig_size_from_screen() -> tuple:
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