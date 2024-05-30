from shapely.geometry import Point, LineString, Polygon, LinearRing


class Polygon:
    def __init__(self):
        i = 0

    def calculate_polygon(self, coords):
        """Determina el tipo de geometria de la libreria Shapely

        Parametros:
        coords -- Lista de coordenadas

        Devuelve:
        Shapely Geometry
        """
        if len(coords) == 1:
            # Crear un Point
            return Point(coords[0])
        elif len(coords) == 2:
            # Crear un LineString
            return LineString(coords)
        elif len(coords) >= 3:
            if coords[0] == coords[-1]:
                # Crear un Polygon si el primero y el último punto son iguales
                return Polygon(coords)
            else:
                # Si tiene tres coordenadas pero no se cierra, consideramos mejor un LineString
                if len(coords) == 3:
                    return LineString(coords)
                # Crear un LinearRing si hay 4 o más puntos y no se cierra
                return LinearRing(coords)
            
            
    def calculate_intersection(self, geometry1, geometry2):
        """
        Calculate the intersection between two geometries.
        """
        if isinstance(geometry1, Polygon) and isinstance(geometry2, Polygon):
            if geometry1.intersects(geometry2):
                return geometry1.intersection(geometry2)
            else:
                return None
        elif isinstance(geometry1, LinearRing) and isinstance(geometry2, LinearRing):
            if geometry1.intersects(geometry2):
                return geometry1.intersection(geometry2)
            else:
                return None
        else:
            raise ValueError("Both geometries should be Polygon or LinearRing.")