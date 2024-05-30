

class Node:

    def __init__(self, parameters, instance, id):
        self.parameters = parameters
        self.instance = instance
        self.id = id
        self.create_node()

    def create_node(self):
        node = self.instance.nodes_df[self.instance.nodes_df['Id'] == self.id]
        self.name = node['Name'].values[0]
        self.address = node['Address'].values[0]
        self.location = node['Location'].values[0]
        self.province = node['Province'].values[0]
        self.zip_code = node['Zip_Code'].values[0]
        self.items = node['Items'].values[0]
        self.weight = node['Weight'].values[0]
        self.node_type = node['Node_Type'].values[0]
        self.tw_start = node['TW_Start'].values[0]
        self.tw_end = node['TW_End'].values[0]
        self.latitude = node['Latitude'].values[0]
        self.longitude = node['Longitude'].values[0]
        self.email = node['Email'].values[0]
        self.phone = node['Phone'].values[0]

    def __str__(self) -> str:
        return 'Node: ' + str(self.id) + ' Name: ' + str(self.name) + ' Items: ' + str(self.items) + ' Coords: ' + str(self.latitude) +  ', ' + str(self.longitude)