from utils import IO

class Validation:

    def __init__(self, parameters, instance, solution):
        self.IO = IO()
        self.parameters = parameters
        self.instance = instance
        self.solution = solution
        self.isValid = True


    def validate(self):
        """
        Validate Solution
        """

        # Input Data
        total_items = self.instance.nodes_df['Items'].sum()
        total_weight = self.instance.nodes_df['Weight'].sum()
        total_nodes = len(self.instance.nodes_df)
        total_vehicles = len(self.instance.fleet_df)

        # Output Data
        total_result_items = self.solution.result_df['Items'].sum()
        total_result_weight = self.solution.result_df['Weight'].sum()
        total_result_nodes = len(self.solution.result_df['Id'].unique())

        routes_df_list = self.IO.cluster_dataframe_by_condition(self.solution.result_df, 'Vehicle')
        total_routes = len(routes_df_list)

        print('Input Nodes:', total_nodes, ' Output Nodes:', total_result_nodes)
        print('Input Items:', total_items, ' Output Items:', total_result_items)
        print('Input Weight:', total_weight, ' Output Weight:', total_result_weight)
        print('Input Vehicles:', total_vehicles, ' Output Routes:', total_routes)
        
        for route_df in routes_df_list:
            route_load = route_df['Items'].sum()
            vehicle_name = route_df['Vehicle'].values[0]
            vehicle_df = self.instance.fleet_df[self.instance.fleet_df['Name'] == vehicle_name]
            vehicle_capacity = vehicle_df['Capacity'].values[0]
            
            # Capacity Check
            if vehicle_capacity < route_load:
                print('\tERROR Vehiculo:', vehicle_name, ' con capcidad:', vehicle_capacity, ' lleva mas carga de la permitida:', route_load)
                self.isValid = False

        print('Es valida la solucion:', self.isValid)



    def __str__(self) -> str:
        return 'Validation:' + str(self.isValid)