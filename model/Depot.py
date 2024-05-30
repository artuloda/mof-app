


class Depot:

    def __init__(self, parameters, instance, id):
        self.parameters = parameters
        self.instance = instance
        self.id = id


    def __str__(self) -> str:
        return 'Depot: ' + str(self.id) + 'Name: ' + str(self.name) + ' Latitude: ' + str(self.capacity) + ' Longitude: ' + str(self.vehicle_type)