


class Vehicle:

    def __init__(self, parameters, instance, id):
        self.parameters = parameters
        self.instance = instance
        self.id = id
        self.create_vehicle()

    def create_vehicle(self):
        vehicle = self.instance.fleet_df[self.instance.fleet_df['Id'] == self.id]
        self.name = vehicle['Name'].values[0]
        self.capacity = vehicle['Capacity'].values[0]
        self.tw_start = vehicle['TW_Start'].values[0]
        self.tw_end = vehicle['TW_End'].values[0]
        self.vehicle_type = vehicle['Vehicle_Type'].values[0]

    def __str__(self) -> str:
        return 'Vehicle: ' + str(self.id) + 'Name: ' + str(self.name) + ' Capacity: ' + str(self.capacity) + ' Type: ' + str(self.vehicle_type)