import networkx as nx
import json
from node import Node


class Graph:
    def __init__(self, filename : str):
        self.nx_graph = nx.DiGraph()
        self.start_node = None
        self.end_node = None
        self.nodes = {}  # Store Node objects keyed by their names
        self.name = filename.split("/")[-1]  # Extract name from filename
        self._load_from_file(filename)

    def _load_from_file(self, filename : str) -> None:
        print("[INFO] Loading graph file...")

        with open(filename, 'r', encoding='utf-8') as file:

            data_graph = json.load(file)
            # Load nodes and edges
            for node, data_entry in data_graph.items():

                if node not in ["start", "end"]:
                    neighbors = data_entry[:-1]
                    heuristic = data_entry[-1]

                    if node not in self.nodes:
                        # Create a new Node object and store it in the nodes dictionary
                        self.nodes[node] = Node(node, heuristic=heuristic)
                    else:
                        # Update the heuristic if the node already exists (it was previously added as a neighbor)
                        self.nodes[node].heuristic = heuristic
                    self.nx_graph.add_node(self.nodes[node])

                    for connection in neighbors:
                        neighbor, weight = connection[0], connection[1]
                        if neighbor not in self.nodes:
                            self.nodes[neighbor] = Node(neighbor)
                        self.nx_graph.add_edge(self.nodes[node], self.nodes[neighbor], weight=weight)

            # Load start and end nodes
            self.start_node = self.nodes[data_graph["start"]]
            self.end_node = self.nodes[data_graph["end"]]
            print("[INFO] Graph file loaded!")

    def get_neighbors(self, node):
        """
        Returns a list of neighbors of a given node.
        """
        return list(self.nx_graph.neighbors(node))

    def get_cost(self, node1, node2):
        """
        Returns the cost (weight) between two given nodes.
        """
        return self.nx_graph[node1][node2]['weight']

    def get_graph_name(self):
        """
        Returns the name of the graph.
        """
        return self.name
