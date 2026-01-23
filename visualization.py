import os
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import random
from networkx.drawing.nx_agraph import graphviz_layout
from config import node_colors
import tkinter as tk

def calculate_graph_layout(G: nx.Graph, min_h_distance: float = 1.5, min_v_distance: float = 2.0, iterations: int = 15) -> dict:
    """
    Calculates the (x, y) positions for a DAG, handling 'long edges' with dummy nodes.
    """
    
    # 1. lépés: Gráf struktúra és Rétegek meghatározása
    # (Ez ugyanaz, mint eddig, csak most a networkx gráfot használjuk közvetlenül)
    adj, rev_adj = _build_graph_structure(G)
    max_layer, nodes_by_layer, layer_map = _assign_layers(G, rev_adj)
    
    # 2. lépés: Virtuális (Dummy) node-ok beszúrása a hosszú élekhez
    # Ez a "titkos összetevő", ami helyet csinál az átívelő éleknek.
    aug_adj, aug_rev_adj, aug_nodes_by_layer, dummies = _insert_dummy_nodes(
        adj, rev_adj, nodes_by_layer, layer_map
    )
    
    # 3. lépés: Kezdeti pozíciók
    positions = _initialize_positions(aug_nodes_by_layer, max_layer, min_h_distance, min_v_distance)
    
    # 4. lépés: Optimalizálás (Barycenter módszer) a kibővített gráfon
    _optimize_node_order(aug_nodes_by_layer, aug_adj, aug_rev_adj, positions, min_h_distance, max_layer, iterations)
    
    # 5. lépés: Koordináták véglegesítése (kivesszük a dummy-kat)
    final_coordinates = _finalize_coordinates(aug_nodes_by_layer, positions, min_h_distance, max_layer, dummies)
    
    return final_coordinates

# --- Segédfüggvények ---

def _build_graph_structure(G):
    adj = {n: [] for n in G.nodes()}
    rev_adj = {n: [] for n in G.nodes()}
    for u, v in G.edges():
        adj[u].append(v)
        rev_adj[v].append(u)
    return adj, rev_adj

def _assign_layers(G, rev_adj):
    memo = {}
    
    def get_depth(node, path_stack):
        if node in memo: return memo[node]
        if node in path_stack: return 0 # Cycle
        
        parents = rev_adj[node]
        if not parents:
            return 0
        
        path_stack.append(node)
        max_depth = 0
        for p in parents:
            d = get_depth(p, path_stack)
            if d > max_depth: max_depth = d
        path_stack.pop()
        
        depth = max_depth + 1
        memo[node] = depth
        return depth

    nodes_by_layer = {}
    layer_map = {} # Gyors kereséshez: node -> layer
    max_layer = 0
    
    for node in G.nodes():
        layer = get_depth(node, [])
        layer_map[node] = layer
        if layer not in nodes_by_layer:
            nodes_by_layer[layer] = []
        nodes_by_layer[layer].append(node)
        if layer > max_layer:
            max_layer = layer
            
    return max_layer, nodes_by_layer, layer_map

def _insert_dummy_nodes(adj, rev_adj, nodes_by_layer, layer_map):
    """
    Létrehoz egy "kiterjesztett" gráfot, ahol a hosszú éleket (melyek szintkülönbsége > 1)
    feldarabolja dummy node-okkal.
    """
    # Másolatokat készítünk, mert módosítani fogjuk őket
    aug_adj = {k: list(v) for k, v in adj.items()}
    aug_rev_adj = {k: list(v) for k, v in rev_adj.items()}
    aug_nodes_by_layer = {k: list(v) for k, v in nodes_by_layer.items()}
    
    dummies = set() # Nyilvántartjuk, melyek a virtuális pontok
    
    # Végigmegyünk az összes EREDETI élen
    for u, neighbors in adj.items():
        for v in neighbors:
            layer_u = layer_map[u]
            layer_v = layer_map[v]
            
            # Ha az él több mint 1 szintet ugrik (pl. 0 -> 2)
            if layer_v > layer_u + 1:
                # Az eredeti közvetlen kapcsolatot töröljük a kiterjesztett gráfban
                # (de vigyázzunk, a ciklus miatt az eredeti adj-on iterálunk, de az aug-ot módosítjuk)
                if v in aug_adj[u]: aug_adj[u].remove(v)
                if u in aug_rev_adj[v]: aug_rev_adj[v].remove(u)
                
                # Lánc építése: u -> d1 -> d2 -> ... -> v
                current_source = u
                
                for k in range(layer_u + 1, layer_v):
                    dummy_node = f"__dummy_{u}_{v}_{k}" # Egyedi név
                    dummies.add(dummy_node)
                    
                    # Hozzáadás a réteghez
                    if k not in aug_nodes_by_layer: aug_nodes_by_layer[k] = []
                    aug_nodes_by_layer[k].append(dummy_node)
                    
                    # Gráf élek frissítése (láncolás)
                    if current_source not in aug_adj: aug_adj[current_source] = []
                    aug_adj[current_source].append(dummy_node)
                    
                    aug_rev_adj[dummy_node] = [current_source]
                    aug_adj[dummy_node] = [] # Init
                    
                    current_source = dummy_node
                
                # Utolsó dummy összekötése a céllal
                aug_adj[current_source].append(v)
                aug_rev_adj[v].append(current_source)
                
    return aug_adj, aug_rev_adj, aug_nodes_by_layer, dummies

def _initialize_positions(nodes_by_layer, max_layer, min_h_dist, min_v_dist):
    positions = {}
    for l in range(max_layer + 1):
        if l in nodes_by_layer:
            for i, node in enumerate(nodes_by_layer[l]):
                positions[node] = {'x': i * min_h_dist, 'y': -l * min_v_dist}
    return positions

def _optimize_node_order(nodes_by_layer, adj, rev_adj, positions, min_h_dist, max_layer, iterations):
    # Ugyanaz a Barycenter logika, de most már a dummy node-okat is rendezgeti
    for _ in range(iterations):
        # Down (szülők szerint)
        for l in range(1, max_layer + 1):
            _barycenter_pass(l, nodes_by_layer, rev_adj, positions, min_h_dist)
        # Up (gyerekek szerint)
        for l in range(max_layer - 1, -1, -1):
            _barycenter_pass(l, nodes_by_layer, adj, positions, min_h_dist)

def _barycenter_pass(layer, nodes_by_layer, neighbors_map, positions, min_h_dist):
    if layer not in nodes_by_layer: return
    nodes = nodes_by_layer[layer]
    new_order = []
    
    for node in nodes:
        neighbors = neighbors_map.get(node, [])
        if not neighbors:
            new_order.append((positions[node]['x'], node))
        else:
            avg = sum(positions[n]['x'] for n in neighbors) / len(neighbors)
            new_order.append((avg, node))
            
    new_order.sort(key=lambda x: x[0])
    
    for i, (avg, node) in enumerate(new_order):
        positions[node]['x'] = i * min_h_dist
    
    nodes_by_layer[layer] = [n for _, n in new_order]

def _finalize_coordinates(nodes_by_layer, positions, min_h_dist, max_layer, dummies):
    final_coords = {}
    max_width = 0
    layer_widths = {}
    
    # 1. Szélességek számolása (dummykkal együtt, mert ők is foglalják a helyet!)
    for l in range(max_layer + 1):
        if l not in nodes_by_layer: continue
        nodes = nodes_by_layer[l]
        width = (len(nodes) - 1) * min_h_dist
        layer_widths[l] = width
        if width > max_width: max_width = width
        
    # 2. Középre igazítás és dummy szűrés
    for l in range(max_layer + 1):
        if l not in nodes_by_layer: continue
        nodes = nodes_by_layer[l]
        offset = (max_width - layer_widths[l]) / 2
        
        # A sorrend a _optimize_node_order miatt már jó
        for i, node in enumerate(nodes):
            if node in dummies:
                continue # A dummy koordinátáját nem adjuk vissza (vagy opcionális)
            
            x = (i * min_h_dist) + offset
            y = positions[node]['y']
            final_coords[node] = (x, y)
            
    return final_coords

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