import networkx as nx
import matplotlib.pyplot as plt
import json


class Graph:
    def __init__(self):
        self.graph = nx.Graph()
        self.graph_json = None


    def add_node(self, node, position, node_color):
        """
        """
        self.graph.add_node(node, pos=position, color=node_color)


    def add_nodes(self, graph_nodes_tuples_list):
        """
        """
        self.graph.add_nodes_from(graph_nodes_tuples_list)

 
    def add_edge(self, node1, node2, distance):
        """
        """
        self.graph.add_edge(node1, node2, weight=distance)


    def add_edges(self, graph_edges_tuples_list):
        """
        """
        self.graph.add_edges_from(graph_edges_tuples_list)


    def add_weighted_edges(self, graph_edges_tuples_list):
        """
        """
        self.graph.add_weighted_edges_from(graph_edges_tuples_list)


    def create_result_json_graph(self):
        """
        Creates Graph Json to represent it in the web in Flask
        """
        nodes = [{'id': node, 'label': str(node), 'color': self.graph.nodes[node]['color']} for node in self.graph.nodes()]
        edges = [{'from': u, 'to': v, 'weight': self.graph[u][v]['weight']} for u, v in self.graph.edges()]

        data = {'nodes': nodes, 'edges': edges}
        self.graph_json = json.dumps(data, ensure_ascii=False)

    
    def show_graph(self):
        """
        Drawing the graph with colored nodes and labels
        """
        pos = nx.get_node_attributes(self.graph, 'pos')
        node_colors = [self.graph.nodes[node]['color'] for node in self.graph.nodes()]
        labels = {node: node for node in self.graph.nodes()}

        nx.draw(self.graph, pos, node_color=node_colors, labels=labels, with_labels=True, node_size=50, font_size=8)
        # plt.show()