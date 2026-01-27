import os
import geopandas as gpd
import pandas as pd
import networkx as nx
from visualization import visualize_graph
from utility import write_graph_to_file

def grouping(gdb_path: str) -> dict[str, pd.DataFrame]:
    gdb_name = "HydroRIVERS_v10_gr.gdb"
    layer_name = gdb_name[:-4]
    gdf = gpd.read_file(gdb_path, layer=layer_name)

    cols_to_keep = ["HYRIV_ID", "NEXT_DOWN", "MAIN_RIV", "LENGTH_KM"]

    river_network_dict = {}
    for value, subset in gdf.groupby('MAIN_RIV'):
        if len(subset) > 1:  # it has to be at least two elements
            df = subset[cols_to_keep]
            river_network_dict[value] = df.reset_index(drop=True)            

    return river_network_dict

def put_mouth_first(group: dict[int, pd.DataFrame]) -> dict[int, pd.DataFrame]:
    new_groups = {}
    for river_id, subset in group.items():
        
        df = subset.copy()
        mouth_rows = df[df["NEXT_DOWN"] == 0]

        if not mouth_rows.empty:
            df = pd.concat([mouth_rows, df[df["NEXT_DOWN"] != 0]])
        
        new_groups[river_id] = df.reset_index(drop=True)
    return new_groups

def check_problems(groups: dict[int, pd.DataFrame]) -> list[tuple[str, str]]:
    problems = []
    for river_id, subset in groups.items():
        # Ellenőrizzük, van-e torkolat (NEXT_DOWN == 0)
        mouth_rows = subset[subset["NEXT_DOWN"] == 0]
        if mouth_rows.empty:
            problems.append((river_id, "There is no NEXT_DOWN=0 row"))
            continue

    return problems

def get_source_node_by_edge(G: nx.DiGraph, edge_id: int) -> int:
    for u, v, data in G.edges(data=True):
        if data.get("id") == edge_id:
            return u
    raise ValueError(f"Edge with id {edge_id} not found.")

def graph_builder(groups: dict[int, pd.DataFrame]) -> dict[int, nx.DiGraph]:
    graph_dict = {}
    for river_network_id, river_network_df in groups.items():
        G = nx.DiGraph()
        
        nx.set_node_attributes(G, False, name='has_sensor')
        
        
        node_set = set(river_network_df["HYRIV_ID"]) | set(river_network_df["NEXT_DOWN"])
        node_list = list(node_set)
        node_list.sort()
        
        node_dict = {}
        for id, counter in zip(node_list, range(0, len(node_list))):
            node_dict[id] = counter
        
        for _, row in river_network_df.iterrows():
            
            hyriv_id = row["HYRIV_ID"]
            next_down = row["NEXT_DOWN"]

            G.add_edge(node_dict[hyriv_id], node_dict[next_down], id=row["HYRIV_ID"], weight=round(row["LENGTH_KM"], 2))

        graph_dict[river_network_id] = G
            
    return graph_dict

    
gdb_path = "datasets/HydroRIVERS_v10_gr.gdb"
river_network_dict = grouping(gdb_path)

problems = check_problems(river_network_dict)
print(f"There is {len(problems)} problematic river network.")
for river_id, issue in problems[:10]:
    print(river_id, issue)
    
graph_dict = graph_builder(river_network_dict)

folder = "predefined graphs"

for key, graph in graph_dict.items():
    # from utility import node_categoryzer
    # node_categoryzer(graph)
    title = f"River Network {key}"
    filename = title.replace(" ", "_")
    write_graph_to_file(graph, filename)    
    visualize_graph(graph, title=title, save=True)
    

#visualize_graph(graph_dict[90000136])

#print(graph_dict[90000136].nodes(data=True))
# visualize_graph(graph_dict[90000136])

#one_river_network = river_network_dict[90000136]
# #another_river_network = river_network_dict[list(river_network_dict.keys())[6]]

