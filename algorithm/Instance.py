from utils import IO, Geo

from scipy.spatial.distance import cdist

class Instance:

    def __init__(self, parameters):  
        self.IO = IO()
        self.Geo = Geo()
        self.parameters = parameters
        self.nodes_df = self.create_nodes_info()
        self.fleet_df = self.create_fleet_info()
        self.distance_matrix = self.create_distance_matrix()

    def create_nodes_info(self):
        """
        Create node input data
        
        Output:
            - nodes_df
        """
        not_included_regions = [4, 5, 18, 19] #Canarias, baleares, ceuta y melilla
        input_df = self.IO.read_csv(file_path=self.parameters.input_file_path + self.parameters.input_file_name, separator=',', decimal='.', encoding='utf-8')

        node_list = list()
        node_counter = 0

        # Add depot
        node_object = [node_counter, 'Depot', 'C. Tajo, s/n', 'Villaviciosa de Odon', 'MADRID', '28670', 0, 0, 'Depot', '00:00', '00:00', 40.37387062578713, -3.919575039549291, '', '']
        node_list.append(node_object)
    
        for index, node in input_df.iterrows():     
            node_name = node['NOMBRE']
            address = node['DIRECCION']
            location = node['MUNICIPIOS']
            province = node['PROVINCIAS']
            zip_code = node['CODPOSTAL']
            items = node['NCAMAS']
            if items == 0:
                continue
            weight = round(int(items) * 120.56, 2)
            node_type = node['FINALIDAD_ASISITENCIAL']
            tw_start = '03:00'
            tw_end = '23:59'
            latitude = node['Y']
            longitude = node['X']
            email = node['EMAIL']
            try:
                phone = str(int(node['TELEFONO']))
            except ValueError as e:
                phone = ''
            region_id = int(node['CODAUTO'])

            if node_counter > 800: # COMMENT
                break

            if not region_id in not_included_regions:
                node_counter = node_counter + 1
                node_object = [node_counter, node_name, address, location, province, zip_code, items, weight, node_type, tw_start, tw_end, latitude, longitude, email, phone]
                node_list.append(node_object)
                
        columns_name = ['Id', 'Name', 'Address', 'Location' , 'Province', 'Zip_Code', 'Items', 'Weight', 'Node_Type', 'TW_Start', 'TW_End', 'Latitude', 'Longitude', 'Email', 'Phone']
        nodes_df = self.IO.create_CSV_from_list(node_list, columns_name, 'input_files/nodes')
        return nodes_df
    

    def create_fleet_info(self):
        """
        Create fleet input data
        
        Output:
            - fleet_df
        """
        fleet_df = self.IO.read_csv(file_path=self.parameters.input_file_path + self.parameters.fleet_file_name, separator=';', decimal=',', encoding='latin-1')
        return fleet_df
    

    # Function to create a distance matrix using geodesic distance
    def create_distance_matrix(self):
        """
        Creates the distance matrix between all pairs of nodes.
        """
        print("Creating distance matrix...")
        coordinates = self.nodes_df[['Latitude', 'Longitude']].values
        def dist_func(u, v):
            return self.Geo.calculate_distance((u[0], u[1]), (v[0], v[1]))
        distance_matrix = cdist(coordinates, coordinates, metric=dist_func)
        return distance_matrix
    
