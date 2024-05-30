import os
import json
import pandas as pd
import random
import folium
import base64
from folium.plugins import MarkerCluster, Search, MeasureControl, LocateControl, MiniMap, FeatureGroupSubGroup, Fullscreen, AntPath, PolyLineOffset, HeatMap, StripePattern, Geocoder, BeautifyIcon


class Folium:
    def __init__(self):
        i = 0

    def get_input_colors(self, colors_dataframe, high_contrast):
        """Devuelve una lista con los colores en formato Hexadecimal en orden aleatorio."""
        if not high_contrast:
            colors = colors_dataframe['HexCode'].values.tolist()
        else:
            colors = colors_dataframe[colors_dataframe['ContrastChk'] == 1]['HexCode'].values.tolist()
        random.shuffle(colors)
        return colors


    def get_node_color(self, index_color, colors):
        """Devuelve el color en la posicion dada. Si el indice esta fuera de la lista, devuelve el correspondiente a la posicion 0."""
        return colors[index_color], (index_color + 1) % len(colors)


    def initialize_folium_map(self, center_coords, logo_img_file):
        """
        Creates a folium map in a html file.

        Parameters:
        logo_img_file -- Ruta del logo a mostrar en el marcador

        Return:
        map_object -- Objeto Folium que se exporta como fichero HTML
        """
        
        map_object = folium.Map(location=center_coords, tiles="OpenStreetMap", zoom_start=10, control_scale=True)
        Fullscreen(position='topleft', title="Expand me", title_cancel="Exit me").add_to(map_object)
        self.add_logo_to_markers(logo_img_file, map_object)
        return map_object


    def create_folium_map(self, file_name, map_object):
        """Creates a folium map in a html file.

        Parameters:
        file_name -- Nombre del fichero (sin tipo de fichero)
        map_object -- Objeto Folium que se exporta como fichero HTML
        """
        folium.TileLayer('openstreetmap', name='Open Street Map').add_to(map_object)
        folium.TileLayer('cartodbpositron', name='Carto BD Positron').add_to(map_object)
        folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr='Esri',name='Esri Satellite').add_to(map_object)
        folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',attr='Esri',name='Esri World Topographic Map').add_to(map_object)
        MiniMap(tile_layer='Cartodb dark_matter', position='bottomleft', toggle_display=True).add_to(map_object)
        MeasureControl(position='bottomleft').add_to(map_object)
        Geocoder(position='topleft', collapsed=True, placeholder="Geocoder Folium").add_to(map_object)
        folium.LayerControl(collapsed=False).add_to(map_object)
        folium.LatLngPopup().add_to(map_object)  # Cuando pinchas te da lat long

        print("Creating File MAP: ", file_name)
        map_object.save(file_name + '.html')
        print("File MAP: ", file_name, ' created.')


    def create_marker(self, location, popup, tooltip_folium, node_name, icon, folium_layer):
        """
        Creates Folium Marker

        Parametros:
        location -- Array [latitude, longitude]
        popup -- Folium pop up object
        tooltip_folium -- String shown when hover over the marker
        node_name -- Marker Id, if we add search
        icon -- Folium icon object
        folium_layer -- Folium layer
        """
        folium.Marker(location=location, popup=popup, tooltip=tooltip_folium, name=node_name, icon=icon).add_to(folium_layer)


    def create_icon(self, icon_name, icon_color, color):
        """
        Creates a Folium Icon

        Parametros:
        icon_name -- Hexadecimal color of the node
        icon_color -- Hexadecimal color of the node
        color -- Folium Color for the marker. ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
        prefix -- Prefix if we use FontAwesome Markers
        angle -- Angle of the icon: 45, 90, 135, 180.

        Return:
        icon -- Folium Icon
        """
        icon = folium.Icon(color=color, icon=icon_name, icon_color=icon_color)
        # if prefix == None:
        #     icon = folium.Icon(color=color, icon=icon_name, icon_color=icon_color, angle=angle)
        # else:
        #     icon = folium.Icon(color=color, icon=icon_name, icon_color=icon_color, prefix=prefix, angle=angle)
        return icon


    def create_circle_icon(self, color, number):
        """
        Creates a Folium Circle Icon With Number

        Parametros:
        color -- Hexadecimal color of the node
        number -- Number inside the marker

        Return:
        icon -- Folium Circle Icon With Number
        """
        icon = BeautifyIcon(border_color=color,text_color=color,number=number,inner_icon_style="margin-top:0;")
        return icon
    
    
    def create_pop_up(self, html, max_width):
        """
        Creates a Folium Pop Up.

        Parametros:
        html -- HTML Code within the pop up

        Return:
        pop_up -- Folium Pop Up
        """
        pop_up = folium.Popup(folium.Html(html, script=True), max_width=max_width)
        return pop_up
    

    def add_logo_to_markers(self, logo_img_file, map_object):
        """
        Adds logo to HTML Table Markers

        Parametros:
        logo_img_file -- Ruta del logo a mostrar en el marcador
        map_object -- Objeto Folium que se exporta como fichero HTML
        """
        encoded_img_file = base64.b64encode(open(logo_img_file, 'rb').read()).decode()
        html = """
        <style>
            .CompanyLogo {
                background-image: url(data:image/png;base64,""" + encoded_img_file + """);
                    width: 150px;  
                    height: 100px; 
                    background-position: center center; 
                    background-repeat: no-repeat; 
                    background-size: contain; 
            }
        </style>
        """
        map_object.get_root().html.add_child(folium.Element(html))


    def add_beggining_HTML_table(self, node_id):
        """
        Crea el principio de una tabla html con formato
        """
        html = """
        <!DOCTYPE html>
        <html>  
        <head><meta charset="latin-1"></head>
        <center><figure><div class="CompanyLogo" width=80></div></figure></center>
        <center><h4 style="font-family: 'system-ui'"; font-size: "11px"; "margin-bottom:5">{}</h4>""".format(node_id) + """</center>
        <center> <table style="height: 126px; width: 305px;">
        <tbody>
        """
        return html


    def add_end_HTML_table(self):
        """
        Crea el final de una tabla html con formato
        """
        html = """</tbody></table></center>
        <center><strong>hosted by <span style="font-family: 'system-ui'; font-size: 30px; color:#36454F">{}</span>""".format('Route66') + """</strong></center>
        </html>"""
        return html
    
    
    def add_end_HTML_table_with_graph(self, graph_img_html):
        """
        Crea el final de una tabla html con formato y un grafico 
        """
        html = """</tbody></table></center>"""
        html = html + graph_img_html # Al terminar la tabla, meto la imagne con el grafico generada
        html = html + """<center><strong>hosted by <span style="font-family: 'system-ui'; font-size: 30px; color:#36454F">{}</span>""".format('Route66') + """</strong></center></html>"""
        return html


    def add_row_to_HTML_table(self, text_name, text_value, units, left_col_color, right_col_color):
        """Crea una fila de una tabla en formato HTML con el texto y los colores por parametro."""
        if units == None:
            html = """
            <tr style="border: 1px solid #dddddd">
                <td style="background-color: """+ left_col_color +""";font-family: 'system-ui';font-size: 11px;"><span style="color: #ffffff;">&nbsp;<strong>""" + str(text_name) + """</strong></span></td>
                <td style="width: 150px;background-color: """+ right_col_color +""";">&nbsp;""" + str(text_value) + """</td>
            </tr>"""
        else:
            html = """
            <tr style="border: 1px solid #dddddd">
                <td style="background-color: """+ left_col_color +""";font-family: 'system-ui';font-size: 11px;"><span style="color: #ffffff;">&nbsp;<strong>""" + str(text_name) + """</strong></span></td>
                <td style="width: 150px;background-color: """+ right_col_color +""";">&nbsp;""" + str(text_value) + ' ' + str(units) +"""</td>
            </tr>"""
        return html


    def add_polygon_to_map(self, feature_collection, folium_layer, polygon_color, tooltip_folium, polygon_id):
        """Add un poligono GeoJon a un objeto Folium."""
        style_function=lambda x, fillColor=polygon_color: {
            "fillColor": fillColor,
            "color": "black",
            "weight": 0.8,
            "fillOpacity": 0.3}

        highlight_function=lambda feature: {
            "fillOpacity": 0.8,
            "weight": 0.9}

        folium.GeoJson(feature_collection, tooltip=tooltip_folium, style_function=style_function, highlight_function=highlight_function, name=polygon_id, zoom_on_click=True).add_to(folium_layer)


    def create_feature_group_folium(self, map_object, layer_color, layer_txt, initial_show, dynamic):
        """Crea una capa folium

        Parametros:
        map_object -- (Folium Map) Objeto folium que representa el mapa
        layer_color -- (str) Color en hexadecimal
        layer_txt -- (str) Texto de la capa
        initial_show -- (boolean) True: Se muestra por defecto, False: Aparece desmarcado en la leyenda
        dynamic -- (boolean) True: marcadores dinamicos, False: marcadores estaticos

        Return:
        folium_layer -- (Folium Layer) Objto folium que contiene una capa del mapa
        """
        layer_name = """<span style="font-family: 'system-ui'; font-size: 15px;  color:""" + str(layer_color) + """ ">{txt}</span>"""
        if not dynamic:
            folium_layer = folium.FeatureGroup(name=layer_name.format(txt=layer_txt), show=initial_show).add_to(map_object)
        else:
            folium_layer = MarkerCluster(name=layer_name.format(txt=layer_txt), show=initial_show).add_to(map_object)
        return folium_layer


    def create_feature_subgroup_folium(self, map_object, layer_color, layer_txt, initial_show, folium_layer):
        """Crea una subcapa folium

        Parametros:
        map_object -- (Folium Map) Objeto folium que representa el mapa
        layer_color -- (str) Color en hexadecimal
        layer_txt -- (str) Texto de la capa
        initial_show -- (boolean) True: Se muestra por defecto, False: Aparece desmarcado en la leyenda
        folium_layer -- (Folium Layer) Capa del mapa en la que vamos a introducir la subcapa

        Return:
        subgroup_layer -- (Folium Layer) Objto folium que contiene una subcapa del mapa
        """
        layer_name = """<span style="font-family: 'system-ui'; font-size: 13px;  color:""" + str(layer_color) + """ ">{txt}</span>"""
        subgroup_layer = FeatureGroupSubGroup(folium_layer, layer_name.format(txt=layer_txt),show=initial_show).add_to(map_object)
        return subgroup_layer


    def create_feature_collection_from_list_of_coordinates(self, coordinates_list, feature_collection_name):
        """Crea una representacion JSON de un objeto FeatureCollection que contiene la lista de coordenadas dada."""
        coordinates_reversed = [[lon, lat] for lat, lon in coordinates_list]  # Reverse the order of each coordinate in the list
        # Define the GeoJSON data
        data = {"type": "FeatureCollection",
                "features": [{"type": "Feature",
                            "geometry": {"type": "Polygon",
                                        "coordinates": [coordinates_reversed]},
                            "properties": {"name": feature_collection_name,
                                            "description": "Polygon description"}}]}
        geojson_str = json.dumps(data)  # Convert the dictionary to a JSON string
        return geojson_str


    def add_route_to_map(self, coordinates, line_color, tooltip_folium, folium_layer, line_option):
        """Calcula ruta

        Parametros:
            coordinates -- (List[List[float, float]]) lista de coordenadas
            line_color -- (string) color del nodo
            tooltip_folium -- (string) nombre de la ruta
            folium_layer -- (FeatureGroupSubGroup) TODO
            line_option -- (integer) TODO
        """
        # 1: Polyline, 2:AntPath, 3:PolylineOffSet
        if line_option == 1:
            folium.PolyLine(coordinates, color=line_color, weight=5, tooltip=tooltip_folium).add_to(folium_layer)
        elif line_option == 2:
            AntPath(coordinates, dash_array=[8, 100], delay=800, tooltip=tooltip_folium, color=line_color).add_to(folium_layer)
        elif line_option == 3:
            PolyLineOffset(coordinates, dash_array="5,10", color=line_color, weight=5, tooltip=tooltip_folium, opacity=1).add_to(folium_layer)


    def get_spain_zip_codes(self, folder_path):
        """
        TODO COMMENT
        """
        folder_path = folder_path + 'SPAIN_geojsons'
        files = os.listdir(folder_path) # List all files in the specified folder
        # print("Files in the folder:") # Print the list of files
        # print(files)
        spain_zip_codes_data = dict()
        for file in files:  # Process each file in the folder        
            file_path = os.path.join(folder_path, file) # Construct the full file path
            if os.path.isfile(file_path): # Check if the path is a file (not a directory)           
                with open(file_path, 'r') as geojson_file:  # Perform operations on the file, for example, read its content
                    zip_codes_geojson = json.load(geojson_file)
                    file_name = file.split('.')[0]
                    spain_zip_codes_data[file_name] = zip_codes_geojson
        return spain_zip_codes_data


    def add_heat_map(self, heat_map_data, folium_layer):
        """Crea un mapa de calor y lo asigna a una capa

        Parametros:
            heat_map_data -- (List[List[Latitude, Longitude, Value]]) lista de coordenadas y valor del mapa de calor
            folium_layer -- (FeatureGroupSubGroup) TODO
        """
        HeatMap(heat_map_data).add_to(folium_layer)