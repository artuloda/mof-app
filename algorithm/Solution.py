from model import Population
from utils import IO, Graph, Folium, DataGraph

class Solution:

    def __init__(self, parameters, instance):
        self.IO = IO()
        self.Graph = Graph()
        self.DataGraph = DataGraph()
        self.Folium = Folium()
        self.parameters = parameters
        self.instance = instance
        self.best_solution = None
        self.fitness = None
        self.result_df = None
        self.result_graph_json = None
        self.result_graph_img_html = None
        self.constructive()


    def constructive(self):
        population = Population(self.parameters, self.instance)
        population.construct()
        self.best_solution = population.best_individual
        self.fitness = population.best_fitness

    
    def save_solution(self):
        """
        Save the best solution found in a .csv, create networkx graph and create, graph img  html for visualization with folium.
        """
        self.create_result_dataframe()
        self.create_graph()
        self.create_graph_img_html()
        

    def create_result_dataframe(self):
        """
        Create a pandas dataframe with the result of the algorithm  
        and store it in 'result_df' attribute 
        """
        result_routes_list = []
        for route in self.best_solution.routes:
            vehicle_id = route.vehicle.name
            for node in route.nodes:
                row = {
                'Vehicle': vehicle_id,
                'Id': node.id,
                'Name': node.name,
                'Address': node.address,
                'Location': node.location,
                'Province': node.province,
                'Zip_Code': node.zip_code,
                'Items': node.items,
                'Weight': node.weight,
                'Node_Type': node.node_type,
                'TW_Start': node.tw_start,
                'TW_End': node.tw_end,
                'Latitude': node.latitude,
                'Longitude': node.longitude,
                'Email': node.email,
                'Phone': node.phone,
                }
                result_routes_list.append(row)
        columns_name =['Vehicle', 'Id', 'Name', 'Address', 'Location', 'Province', 'Zip_Code', 'Items', 'Weight', 'Node_Type', 'TW_Start','TW_End', 'Latitude', 'Longitude', 'Email', 'Phone']
        self.result_df = self.IO.create_dataframe(result_routes_list, columns_name)
        self.IO.create_csv(self.result_df, self.parameters.output_file_path + 'results')


    def create_graph(self):
        """
        Generate an Graph object from the data contained into 'result_df'.
        """
        colors_dataframe = self.IO.read_csv(file_path=self.parameters.static_map_path + 'HEXADECIMAL_COLORS.csv', separator=';', encoding='utf-8', decimal=',')
        colors = colors_dataframe[colors_dataframe['ContrastChk'] == 1]['HexCode'].values.tolist()
        routes_df_list = self.IO.cluster_dataframe_by_condition(self.result_df, 'Vehicle')
        index_color = 0
        for route_df in routes_df_list:
            vehicle_name = route_df['Vehicle'].values[0]
            node_color, index_color = self.Folium.get_node_color(index_color, colors)
            route_nodes = route_df['Id'].tolist()
            latitudes = route_df['Latitude'].tolist()
            longitudes = route_df['Longitude'].tolist()

            # Create nodes with position and color attributes
            for node, latitude, longitude in zip(route_nodes, latitudes, longitudes):
                position = (longitude, latitude)
                self.Graph.add_node(node, position, node_color)

            # Create edges with weights
            for i in range(len(route_nodes) - 1):
                distance = self.instance.distance_matrix[route_nodes[i], route_nodes[i + 1]]
                self.Graph.add_edge(route_nodes[i], route_nodes[i + 1], distance)

        # Drawing the graph with colored nodes and labels
        self.Graph.show_graph() 

        # Creates Graph Json to represent it in the web in Flask
        self.Graph.create_result_json_graph()   
        self.result_graph_json = self.Graph.graph_json


    def create_graph_img_html(self):
        """
        Creates an image with the results
        """
        routes_ids = list()
        routes_items = list()
        routes_df_list = self.IO.cluster_dataframe_by_condition(self.result_df, 'Vehicle')
        for route_df in routes_df_list:
            vehicle_name = route_df['Vehicle'].values[0]
            route_items = route_df['Items'].sum()
            routes_ids.append(vehicle_name)
            routes_items.append(route_items)
        self.result_graph_img_html = self.DataGraph.create_matplotlib_graph(routes_ids, routes_items, max_width_pop_up=500)

    def __str__(self) -> str:
        print('Solution:', self.best_solution)