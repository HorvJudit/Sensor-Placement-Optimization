import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from config import node_colors
import tkinter as tk

def visualize_graph(G: nx.Graph) -> None:
      
    # makes the figure size fullscreen (there will be no margins)
    plt.figure(figsize=get_fig_size_from_screen())    
    
    pos = {node: G.nodes[node]['pos'] for node in G.nodes()}    
    colors = [node_colors['sensor'] if G.nodes[node].get('has_sensor', False) else node_colors['default'] for node in G.nodes()]            
    weights = nx.get_edge_attributes(G, 'weight')
            
    nx.draw(G, pos, with_labels=True, node_color=colors, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
    plt.show()
    
    
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