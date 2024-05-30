import math
from geopy.distance import geodesic


class Geo:
    def __init__(self):
        i = 0

    def calculate_distance(self, coord1, coord2):
        """
        Calculates distance in kilometers"""
        return math.ceil(geodesic(coord1, coord2).kilometers)

    def signed_polygon_area(self, vertices):
        """Calcula el area de un poligono utilizando su lista de vertices."""
        num_vertices = len(vertices)
        area = 0

        for i in range(num_vertices):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % num_vertices]
            area += (x1 * y2) - (x2 * y1)
        return area / 2


    def calculate_centroid(self, latitudes, longitudes):
        """Calcula el centroide de una lista de puntos.

        Parametros:
        latitudes -- Lista de latitudes
        longitudes -- Lista de longitudes

        Devuelve:
        Las coordenadas del centroide correspondiente a una lista de puntos.
        """
        vertices = list(zip(latitudes, longitudes))
        num_vertices = len(vertices)
        area = self.signed_polygon_area(vertices)
        if area == 0:
            return vertices[0]

        x_sum = 0
        y_sum = 0

        for i in range(num_vertices):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % num_vertices]
            common_term = (x1 * y2) - (x2 * y1)
            x_sum += (x1 + x2) * common_term
            y_sum += (y1 + y2) * common_term

        center_x = x_sum / (6 * area)
        center_y = y_sum / (6 * area)

        return center_x, center_y


    def get_polygon_shape(self, coords_list):
        """Ordena la lista de coordenadas dada usando su angulo polar."""
        cent = (sum([p[0] for p in coords_list])/len(coords_list), sum([p[1] for p in coords_list])/len(coords_list))  # compute centroid
        coords_list.sort(key=lambda p: math.atan2(p[1]-cent[1], p[0]-cent[0]))  # sort by polar angle
        return coords_list


    def create_list_of_tuples_coordinates(self, latitudes, longitudes):
        """Devuelve una lista de tuplas con las coordenadas correspondientes a enlazar las listas de latitudes y longitudes dadas."""
        coordinates_list = list()
        for pos in range(len(latitudes)):
            coordinate = (float(latitudes[pos]), float(longitudes[pos]))
            coordinates_list.append(coordinate)
        return coordinates_list


    def create_list_of_list_coordinates(self, latitudes, longitudes):
        """Devuelve una lista de listas con las coordenadas correspondientes a enlazar las listas de latitudes y longitudes dadas."""
        coordinates_list = list()
        for pos in range(len(latitudes)):
            coordinate = [float(latitudes[pos]), float(longitudes[pos])]
            coordinates_list.append(coordinate)
        return coordinates_list