from utils import IO, Folium, Geo, Here

class Map:
    def __init__(self, parameters, instance, solution):

        self.IO = IO()
        self.Folium = Folium()
        self.Geo = Geo()
        self.Here = Here()
        
        self.parameters = parameters
        self.instance = instance
        self.solution = solution
        self.create_map_data()


    def create_map_data(self):
        """
        Initialize Data for Map Class
        """
        print("Creating Map Data...")
        self.logo_img_file = self.parameters.static_map_path + 'logo_white.png'
        self.colors_dataframe = self.IO.read_csv(file_path=self.parameters.static_map_path + 'HEXADECIMAL_COLORS.csv', separator=';', encoding='utf-8', decimal=',') # Dataframe con los colores
        self.colors = self.Folium.get_input_colors(self.colors_dataframe, 0) # Lista desordenada de colores en hexadecimal
        self.colors_high_contrast = self.Folium.get_input_colors(self.colors_dataframe, 1) # Lista desordenada de colores en hexadecimal
        self.spain_zip_codes_data = self.Folium.get_spain_zip_codes(self.parameters.static_map_path)

        self.depot_info = self.instance.nodes_df[self.instance.nodes_df['Node_Type'] == 'Depot'].iloc[0]
        self.map_object = self.Folium.initialize_folium_map([self.depot_info['Latitude'], self.depot_info['Longitude']], self.logo_img_file)


    def draw_map(self):
        """
        Main Method: Creates HTML MAP USING FOLIUM
        """
        print("Creating Map...")
        self.draw_zip_codes()
        self.draw_depot()
        self.draw_nodes()
        self.draw_heat_map()
        self.draw_routes()  

        output_file_name = self.parameters.static_map_path + 'result_map'
        self.Folium.create_folium_map(output_file_name, self.map_object) # Guarda el mapa en formato .html y ajusta ciertos parametros del mapa


    def draw_zip_codes(self):
        """
        Draw Zip Code Polygons
        """
        layer_color = '#00008B'
        layer_txt = 'Codigos Postales'
        initial_show = False
        dynamic = False
        zip_codes_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)

        index_color = 0
        for file, geojson in self.spain_zip_codes_data.items():
            if not file in self.parameters.city_name_zip_code_list:
                continue
            polygon_color, index_color = self.Folium.get_node_color(index_color, self.colors_high_contrast)
            for position in range(len(geojson['features'])):
                single_geojson = geojson['features'][position]
                single_geojson_id = single_geojson['properties']['COD_POSTAL']
                tooltip = 'CP:' + str(single_geojson_id) + ' - ' + str(file)
                self.Folium.add_polygon_to_map(single_geojson, zip_codes_layer, polygon_color, tooltip, tooltip)


    def draw_depot(self):
        """
        Add depot into map and add seaborn plot
        """
        depot_info = self.instance.nodes_df[self.instance.nodes_df['Node_Type'] == 'Depot'].iloc[0]
        node_color = '#ADD8E6'

        tooltip_folium = depot_info['Name']
        node_id = depot_info['Id']
        node_name = depot_info['Name']
        address = depot_info['Address']
        location = depot_info['Location']
        province = depot_info['Province']
        zip_code = depot_info['Zip_Code']
        node_type = depot_info['Node_Type']
        latitude = depot_info['Latitude']
        longitude = depot_info['Longitude']
        icon_name = 'home'
        max_width = 500
        graph_img_html = self.solution.result_graph_img_html
        self.add_depot_html(node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, latitude, longitude, icon_name, graph_img_html, max_width)


    def draw_nodes(self):
        """
        Add nodes into map
        """
        nodes_by_province_df_list = self.IO.cluster_dataframe_by_condition(self.instance.nodes_df, 'Province')
        layer_color = '#00008B'
        layer_txt = 'Nodos Totales'
        initial_show = False
        dynamic = True
        index_color = 0
        nodes_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)
        for nodes_by_province_df in nodes_by_province_df_list:
            province = nodes_by_province_df['Province'].values[0]
            node_color, index_color = self.Folium.get_node_color(index_color, self.colors_high_contrast)
            for index, node in nodes_by_province_df.iterrows():
                node_id = node['Id']
                node_name = node['Name']
                address = node['Address']
                location = node['Location']
                province = node['Province']
                zip_code = node['Zip_Code']
                node_type = node['Node_Type']
                items = node['Items']
                weight = node['Weight']
                lat = node['Latitude']
                long = node['Longitude']

                icon_name = self.get_icon_name(node_type)
                #print(node_type, icon_name)
                tooltip_folium = 'Node: ' + str(node_id) + '-' + str(node_name)
                self.add_html_node(nodes_layer, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, items, weight, lat, long, icon_name)

    
    def draw_routes(self):
        """
        Add routes into map
        """
        routes_df_list = self.IO.cluster_dataframe_by_condition(self.solution.result_df, 'Vehicle')
        layer_color = '#25383C' # '#25383C'	DarkSlateGray or DarkSlateGrey (W3C)
        initial_show = False
        dynamic = False
        index_color = 0
        for route_df in routes_df_list:
            vehicle_name = route_df['Vehicle'].values[0]
            route_load = route_df['Items'].sum()
            total_nodes = len(route_df) - 2
            layer_txt = 'Ruta ' + str(vehicle_name) + ' - Carga: ' + str(route_load) + ' Paradas: ' + str(total_nodes)
            route_layer =  self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)
            node_color, index_color = self.Folium.get_node_color(index_color, self.colors_high_contrast)
            latitudes = list()
            longitudes = list()
            stops_counter = 0
            for index, node_df in route_df.iterrows():
                node_id = node_df['Id']
                node_name = node_df['Name']
                address = node_df['Address']
                location = node_df['Location']
                province = node_df['Province']
                zip_code = node_df['Zip_Code']
                node_type = node_df['Node_Type']
                items = node_df['Items']
                weight = node_df['Weight']
                lat = node_df['Latitude']
                long = node_df['Longitude']

                if node_id != 0:
                    latitudes.append(lat)
                    longitudes.append(long)
                    tooltip_folium = 'Node: ' + str(node_id) + '-' + str(node_name)
                    self.add_route_html_node(route_layer, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, items, weight, lat, long, stops_counter)
                stops_counter = stops_counter + 1

            coordinates = self.Geo.create_list_of_list_coordinates(latitudes, longitudes)
            if len(coordinates) > 2:
                route_info_here = self.Here.calculate_route_HERE(coordinates, 'car', self.parameters.here_API_key)
                route_coordinates_here = route_info_here[0]
                route_distance = route_info_here[1]
                route_time = route_info_here[2]
                print('La ruta:', layer_txt, ' tiene una distancia de ', route_distance, ' y un tiempo de ', route_time)
                self.Folium.add_route_to_map(route_coordinates_here, node_color, layer_txt, route_layer, 2)


    def get_icon_name(self, node_type):
        """
        Get Icon Name to show in the folium marker
        """
            
        # icon_dict = {'PSIQUIÁTRICO': 'meh-oh',
        # 'MÉDICO-QUIRÚRGICO': 'user-md',
        # 'GENERAL': 'hospital-o',
        # 'GERIATRÍA Y/O LARGA ESTANCIA': 'ambulance',
        # 'REHABILITACIÓN PSICOFÍSICA': 'wheelchair',
        # 'MATERNO-INFANTIL': 'smile-o',
        # 'QUIRÚRGICO': 'gears',
        # 'INFANTIL': 'lemon-o',
        # 'TRAUMATOLOGÍA Y/O REHABILITACIÓN': 'wheelchair-alt',
        # 'OTROS MONOGRÁFICOS': 'stethoscope',
        # 'OFTÁLMICO U ORL': 'eye',
        # 'ONCOLÓGICO': 'life-buoy',
        # 'OTRA FINALIDAD': 'medkit',
        # 'MATERNAL': 'heart'}

        icon_dict = {'PSIQUIÁTRICO': 'glyphicon-filter',
        'MÉDICO-QUIRÚRGICO': 'glyphicon-plus-sign',
        'GENERAL': 'glyphicon-plus',
        'GERIATRÍA Y/O LARGA ESTANCIA': 'glyphicon-euro',
        'REHABILITACIÓN PSICOFÍSICA': 'glyphicon-cloud',
        'MATERNO-INFANTIL': 'glyphicon-asterisk',
        'QUIRÚRGICO': 'glyphicon-trash',
        'INFANTIL': 'glyphicon-headphones',
        'TRAUMATOLOGÍA Y/O REHABILITACIÓN': 'glyphicon-cog',
        'OTROS MONOGRÁFICOS': 'glyphicon-ice-lolly',
        'OFTÁLMICO U ORL': 'glyphicon-eye-open',
        'ONCOLÓGICO': 'glyphicon-piggy-bank',
        'OTRA FINALIDAD': 'glyphicon-asterisk',
        'MATERNAL': 'glyphicon-piggy-bank',
        'Depot': 'glyphicon-home'}

        try:
            icon_name = icon_dict[node_type]
        except:
            icon_name = 'glyphicon-tint'
        return 'glyphicon-plus-sign' #icon_name
    

    def add_depot_html(self, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, latitude, longitude, icon_name, graph_img_html, max_width):
        """
        Add depot marker to map
        """
        left_col_color_1 = '#36454F' #'#2C3539' # Even row left color
        right_col_color_1 = '#FBFBF9' # Even row right color
        left_col_color_2 = '#36454F' # Odd row left color
        right_col_color_2 = '#FAF5EF' # Odd row right color

        html = self.Folium.add_beggining_HTML_table(node_name)
        html = html + self.Folium.add_row_to_HTML_table('Identificador Nodo', node_id, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Nombre', node_name, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Dirección', address, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Localidad', location, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Provincia', province, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Código Postal', zip_code, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Tipo Nodo', node_type, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Latitud', latitude, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Longitud', longitude, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_end_HTML_table_with_graph(graph_img_html)

        location = [latitude, longitude]
        popup = self.Folium.create_pop_up(html, max_width=max_width)
        tooltip_folium = 'Node: ' + str(node_id)
        color = 'black'
        icon = self.Folium.create_icon(icon_name, node_color, color)
        self.Folium.create_marker(location, popup, tooltip_folium, node_name, icon, self.map_object)


    def add_html_node(self, nodes_layer, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, items, weight, lat, long, icon_name):
        """
        Add node marker to nodes layer
        """
        left_col_color = '#36454F' # Row left color
        right_col_color = '#FBFBF9' # Row right color

        html = self.Folium.add_beggining_HTML_table(node_id)
        html = html + self.Folium.add_row_to_HTML_table('Identificador Nodo', node_id, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Nombre', node_name, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Dirección', address, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Localidad', location, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Provincia', province, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Código Postal', zip_code, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Tipo Nodo', node_type, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Items', items, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Peso', weight, 'kg.', left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Latitud', lat, None, left_col_color, right_col_color)
        html = html + self.Folium.add_row_to_HTML_table('Longitud', long, None, left_col_color, right_col_color)
        html = html + self.Folium.add_end_HTML_table()

        location = [lat, long]
        popup = self.Folium.create_pop_up(html, max_width=500)
        tooltip_folium = 'Node: ' + str(node_id)
        color = 'black'
        icon = self.Folium.create_icon(icon_name, node_color, color)
        self.Folium.create_marker(location, popup, tooltip_folium, node_name, icon, nodes_layer)


    def add_route_html_node(self, route_layer, node_color, tooltip_folium, node_id, node_name, address, location, province, zip_code, node_type, items, weight, lat, long, stops_counter):
        """
        Add node marker from route into route layer
        """
        left_col_color_1 = '#36454F' #'#2C3539' # Even row left color
        right_col_color_1 = '#FBFBF9' # Even row right color
        left_col_color_2 = '#36454F' # Odd row left color
        right_col_color_2 = '#FAF5EF' # Odd row right color

        html = self.Folium.add_beggining_HTML_table(node_name)
        html = html + self.Folium.add_row_to_HTML_table('Identificador Nodo', node_id, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Nombre', node_name, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Dirección', address, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Localidad', location, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Provincia', province, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Código Postal', zip_code, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Tipo Nodo', node_type, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Items', items, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Peso', weight, 'kg.', left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_row_to_HTML_table('Latitud', lat, None, left_col_color_2, right_col_color_2)
        html = html + self.Folium.add_row_to_HTML_table('Longitud', long, None, left_col_color_1, right_col_color_1)
        html = html + self.Folium.add_end_HTML_table()

        location = [lat, long]
        popup = self.Folium.create_pop_up(html, max_width=500)
        tooltip_folium = 'Node: ' + str(node_id)
        icon = self.Folium.create_circle_icon(node_color, stops_counter)
        self.Folium.create_marker(location, popup, tooltip_folium, node_name, icon, route_layer)


    def draw_heat_map(self):
        """
        Draw Heat Map  using Folium library
        """
        layer_color = '#00008B'
        layer_txt = 'Mapa Calor'
        initial_show = False
        dynamic = False
        heat_map_layer = self.Folium.create_feature_group_folium(self.map_object, layer_color, layer_txt, initial_show, dynamic)

        selected_columns = self.instance.nodes_df[['Latitude', 'Longitude', 'Items']]
        heat_map_data = selected_columns.values.tolist() # Convierte estas columnas en una lista de listas
        self.Folium.add_heat_map(heat_map_data, heat_map_layer)