import flexpolyline as fp
import requests
from requests.exceptions import Timeout

class Here:
    def __init__(self):
        i = 0

    def request_url_HERE(self, url_query):
        # """Hace GET al endpoint representado por la url dado hasta que devuelva 200. Despues devuelve un json que representa la respuesta."""
        # response = requests.get(url_query)
        # while response.status_code != requests.codes.ok:  # para respuesta de json distintas de 200
        #     response = requests.get(url_query)
        # data = response.json()
        # return data
        """Hace GET al endpoint representado por la url dado hasta que devuelva 200 o hasta un máximo de 5 segundos. Devuelve un json que representa la respuesta."""
        try:
            response = requests.get(url_query, timeout=5)
            if response.status_code == requests.codes.ok:  # para respuesta de json igual a 200
                return requests.get(url_query).json()
            else:
                # Manejo de otros códigos de estado HTTP aquí, si es necesario
                response.raise_for_status()
        except Timeout:
            # Manejar el error de tiempo de espera aquí
            raise TimeoutError("La solicitud excedió el tiempo máximo de 5 segundos.")
        except requests.RequestException as e:
            # Manejar otros errores de solicitudes aquí
            raise SystemError(f"Error en la solicitud: {e}")


    def calculate_route_HERE(self, coordinates, vehicle, here_API_key):
        """Funcion que llama a la API de HERE usando una lista de nodos y un tipo de vehiculo.

        Parametros:
        coordinates -- Lista de nodos
        vehicle -- Tipo de vehiculo: car, truck
        here_API_key -- Here API KEY

        Devuelve:
        Las coordenadas de la ruta junto a su distancia en KM y su tiempo en horas.
        """
        url = "https://router.hereapi.com/v8/routes?"
        origin_point = coordinates[0]
        origin = "&origin=" + str(origin_point[0]) + "," + str(origin_point[1])  # Punto origen
        destination_point = coordinates[len(coordinates) - 1]
        destination = "&destination=" + str(destination_point[0]) + "," + str(destination_point[1])  # Punto Fin de Ruta
        via = ""
        for pos in range(1, len(coordinates) - 1):  # Trayecto de nodos desde el segundo hasta el penultimo
            point = coordinates[pos]
            via = via + "&via=" + str(point[0]) + "," + str(point[1])

        transport_mode = "&transportMode=" + str(vehicle)
        # url_query = url + origin + destination + via + "!passThrough=true&return=polyline,summary" + "&apikey=" + here_API_key
        url_query = url + origin + transport_mode + destination + via + "&return=polyline,summary" + "&apikey=" + here_API_key
        data_route_response = self.request_url_HERE(url_query)

        route_info = list()
        coords_list = self.get_coordinates_list_from_HERE(data_route_response)
        route_distance, route_time = self.get_route_distance_time_HERE(data_route_response)

        formatted_distance = round(route_distance / 1000, 2)  # FROM M TO KM
        formatted_time = round((route_time / 60) / 60, 2)  # FROM SECONDS TO HOURS
        route_info.append(coords_list)
        route_info.append(formatted_distance)
        route_info.append(formatted_time)
        return route_info


    def get_coordinates_list_from_HERE(self, data_route_response):
        """Processa la polyline de HERE y la pasa a coordenadas."""
        coords_list = list()
        try:
            number_of_polylines = len(data_route_response['routes'][0]['sections'])      
            for section_pos in range(number_of_polylines):
                polyline = data_route_response['routes'][0]['sections'][section_pos]['polyline']
                coords_response = fp.decode(polyline)
                coords_list.extend(coords_response)
        except IndexError as e:
            print(e, " Response:", data_route_response)
        return coords_list


    def get_route_distance_time_HERE(self, data_route_response):
        """Processa la distancia y tiempo de la ruta HERE.

        Parametros:
        data_route_response -- Objeto respuesta de la API de HERE que representa la ruta.

        Devuelve:
        Distancia en metros y tiempo en segundos para una ruta dada.
        """
        route_distance = 0
        route_time = 0
        try:
            number_of_stops = len(data_route_response['routes'][0]['sections'])
            for sectionPos in range(number_of_stops):
                summary_info = data_route_response['routes'][0]['sections'][sectionPos]['summary']
                route_distance = route_distance + summary_info['length']
                route_time = route_time + summary_info['duration']
        except IndexError as e:
            print(e, " Response:", data_route_response)
        return route_distance, route_time


    def geocode_search(self, address, number, population, zip_code, city, current_state, here_api_key):
        """
        Constructs a URL for a geocode search using various location parameters and
        retrieves the geocoding results from the HERE API.

        Parameters:
        - address (str): The street address to geocode.
        - number (str): The house number of the address.
        - population (str): The population/district related to the address.
        - zip_code (str): The postal code of the address.
        - city (str): The city of the address.
        - current_state (str): The state of the address.
        - here_api_key (str): The API key for the HERE API.

        Returns:
        - result (json): The geocoding result in JSON format obtained from the HERE API.
        """
        if number != "":
            url = (
                "https://geocode.search.hereapi.com/v1/geocode?qq=houseNumber="
                + str(number).replace(" ", "+")
                + ";street="
                + str(address).replace(" ", "+")
                + ";city="
                + str(population).replace(" ", "+")
                + ";postalCode="
                + str(zip_code)
                + ";county="
                + str(city)
                + ";state="
                + str(current_state)
                + ";country=España&apiKey="
                + here_api_key
            )
        else:
            url = (
                "https://geocode.search.hereapi.com/v1/geocode?qq=street="
                + str(address).replace(" ", "+")
                + ";city="
                + str(population).replace(" ", "+")
                + ";postalCode="
                + str(zip_code)
                + ";county="
                + str(city)
                + ";state="
                + str(current_state)
                + ";country=España&apiKey="
                + here_api_key
            )
        #print("URL ENVIADA HERE:", url) # TODO BORRAR
        #print("-----") # TODO BORRAR
        result = self.get_url(url)
        #print("RESPUESTAS HERE GEOCODE:", result)
        return result


    def geocode_search_by_name(self, name, address, number, population, zip_code, city, current_state, here_api_key):
        """
        Constructs a URL for a geocode search using various location parameters and
        retrieves the geocoding results from the HERE API.

        Parameters:
        - address (str): The street address to geocode.
        - number (str): The house number of the address.
        - population (str): The population/district related to the address.
        - zip_code (str): The postal code of the address.
        - city (str): The city of the address.
        - current_state (str): The state of the address.
        - here_api_key (str): The API key for the HERE API.

        Returns:
        - result (json): The geocoding result in JSON format obtained from the HERE API.
        """
        if number != "":
            url = (
                "https://geocode.search.hereapi.com/v1/geocode?qq=postalCode="
                + str(zip_code)
                + ";city="
                + str(population).replace(" ", "+")
                + ";street="
                + str(address).replace(" ", "+")
                + ";houseNumber="
                + str(number).replace(" ", "+")
                + ";county="
                + str(city)
                + ";state="
                + str(current_state)
                + ";country=España&limit=10&apiKey="
                + here_api_key
                + "&q="
                + str(name).replace(" ", "+")
            )
        else:
            url = (
                "https://geocode.search.hereapi.com/v1/geocode?qq=postalCode="
                + str(zip_code)
                + ";city="
                + str(population).replace(" ", "+")
                + ";street="
                + str(address).replace(" ", "+")
                + ";county="
                + str(city)
                + ";state="
                + str(current_state)
                + ";country=España&limit=10&apiKey="
                + here_api_key
                + "&q="
                + str(name).replace(" ", "+")
            )
        #print("URL ENVIADA HERE:", url) # TODO BORRAR
        #print("-----") # TODO BORRAR
        result = self.get_url(url)
        #print("RESPUESTAS HERE GEOCODE:", result)
        return result


    def rev_geocode_search(self, lat, long, here_api_key):
        """
        Constructs a URL for a reverse geocode search using latitude and longitude
        coordinates, and retrieves the results from the HERE API.

        Parameters:
        - lat (float): The latitude coordinate for the reverse geocode search.
        - long (float): The longitude coordinate for the reverse geocode search.
        - here_api_key (str): The API key for the HERE reverse geocode API.

        Returns:
        - result (json): The reverse geocoding result in JSON format obtained from the HERE API.
        """
        url = (
            "https://revgeocode.search.hereapi.com/v1/revgeocode"
            + "?at="
            + str(lat)
            + "%2C"
            + str(long)
            + "&apiKey="
            + here_api_key
        )
        #print("URL ENVIADA HERE:", url) # TODO BORRAR
        #print("-----") # TODO BORRAR
        result = self.get_url(url)
        #print("RESPUESTAS HERE REVGEOCODE:", result)
        return result


    def get_here_info(self, here_result):
        """
        Procesa la consulta a HERE para el geocoder
        """
        try:
            if len(here_result["items"]) != 0:
                location_info = here_result["items"][0]["position"]
                here_lat = self.get_coordinates_info('lat', location_info)
                here_long = self.get_coordinates_info('lng', location_info)

                address_info = here_result["items"][0]["address"]
                city_here = self.get_address_info('city', address_info)
                county_here = self.get_address_info('county', address_info)
                state_here = self.get_address_info('state', address_info)
                country_here = self.get_address_info('countryName', address_info)
                zip_code_here = self.get_address_info('postalCode', address_info)
                address_here = self.get_address_info('label', address_info)
                street_here = self.get_address_info('street', address_info)

                score_info = here_result["items"][0]["scoring"]
                zip_code_here_error = self.get_score("postalCode", score_info)
                city_here_error = self.get_score("city", score_info)
                address_here_error = 0.0 # TODO REVISAR
            else:
                here_lat = 0.0
                here_long = 0.0

                city_here = ''
                county_here = ''
                state_here = ''
                country_here = ''
                zip_code_here = ''
                address_here = ''
                street_here = ''

                zip_code_here_error = 0.0
                city_here_error = 0.0
                address_here_error = 0.0 # TODO REVISAR
        except KeyError:
            here_lat = 0.0
            here_long = 0.0

            city_here = ''
            county_here = ''
            state_here = ''
            country_here = ''
            zip_code_here = ''
            address_here = ''
            street_here = ''

            zip_code_here_error = 0.0
            city_here_error = 0.0
            address_here_error = 0.0 # TODO REVISAR
        return here_lat, here_long, city_here, county_here, state_here, country_here, zip_code_here, address_here, street_here, zip_code_here_error, city_here_error, address_here_error


    def get_here_info_rev_geocoder(self, here_result):
        """
        """
        try:
            if len(here_result["items"]) != 0:
                #print(here_result["items"][0])
                address_info = here_result["items"][0]["address"]
                rev_city_here = self.get_address_info('city', address_info)
                rev_county_here = self.get_address_info('county', address_info)
                rev_state_here = self.get_address_info('state', address_info)
                rev_country_here = self.get_address_info('countryName', address_info)
                rev_zip_code_here = self.get_address_info('postalCode', address_info)
                rev_address_here = self.get_address_info('label', address_info)
                rev_street_here = self.get_address_info('street', address_info)
            else:
                rev_city_here = ''
                rev_county_here = ''
                rev_state_here = ''
                rev_country_here = ''
                rev_zip_code_here = ''
                rev_address_here = ''
                rev_street_here = ''
        except KeyError:
            rev_city_here = ''
            rev_county_here = ''
            rev_state_here = ''
            rev_country_here = ''
            rev_zip_code_here = ''
            rev_address_here = ''
            rev_street_here = ''
        return rev_city_here, rev_county_here, rev_state_here, rev_country_here, rev_zip_code_here, rev_address_here, rev_street_here


    def get_coordinates_info(self, coordinates_metric_name, location_info):
        """
        Inputs:
            - Location metric name
            - Location Info
        Output:
            - Geocoder response from API HERE
        """
        try:
            return location_info[coordinates_metric_name]
        except KeyError:
            return 0.0


    def get_address_info(self, address_metric_name, address_info):
        """
        Inputs:
            - Address metric name
            - Address Info
        Output:
            - Geocoder response from API HERE
        """
        try:
            return address_info[address_metric_name]
        except KeyError:
            return ''


    def get_score(self, score_metric_name, score_info):
        """
        Inputs:
            - ScoreMetricName
            - Score Info
        Output:
            - Geocoder response from API HERE
        """
        try:
            return score_info["fieldScore"][score_metric_name]
        except KeyError:
            return 0.0


    def get_url(self, url):
        """
        Make HERE API call
        """
        response = requests.get(str(url))
        data = response.json()
        return data