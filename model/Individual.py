import random
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sklearn.cluster import KMeans
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import fcluster, linkage

import model
from utils import Geo

class Individual:

    def __init__(self, parameters, instance):
        self.Geo = Geo()
        self.parameters = parameters
        self.instance = instance
        self.routes = list()
        self.is_valid = False
        self.fitness = None


    # Main function to solve the CVRP
    def solve_cvrp(self, option):
        """
        Solve the Capacitated Vehicle Routing Problem (CVRP) using different techniques.
        
        """
        # print("Start Creating Initial Solution...")
        self.initialize_routes(option)
        # print("End Creating Initial Solution...")

        # print("Start Improving Each Initial Route...")
        self.improve_single_route()
        # print("End Improving Each Initial Route. Current Fitness:", self.fitness)

        # print("Start Improving Routes...")
        self.improve_routes()
        # print("End Improving Routes. Current Fitness:", self.fitness)


    def initialize_routes(self, option):
        """
        Generate an initial feasible solution for the Vehicle Routing Problem using different techniques
        """
        if option == 1:
            routes = self.initialize_routes_hierarchical_clustering()
        elif option == 2:
            routes = self.initialize_routes_compact_kmeans()
        elif option == 3: 
            routes = self.initialize_routes_heuristic()
        elif option == 4: 
            routes = self.initialize_routes_heuristic_min_fleet()
        elif option == 5: 
            routes = self.initialize_routes_nearest_neighbor()
        elif option == 6: 
            routes = self.initial_routes_compact()
        else:
            routes = self.initialize_routes_or_tools()

        # Create Routes Objects
        # print(routes)
        self.create_routes_object(routes)


    def initialize_routes_hierarchical_clustering(self):
        """
        Generate an initial feasible solution for the Vehicle Routing Problem using
        the hierarchical clustering considering vehicles capacities
        """
        # Index of the depot node
        depot_index = self.instance.nodes_df[self.instance.nodes_df['Node_Type'] == 'Depot'].index.item()
        client_indices = self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot'].index.tolist()

        # Ensure we have vehicle IDs in the correct format (assuming they are in self.instance.fleet_df['Id'])
        vehicle_ids = self.instance.fleet_df['Id'].tolist()
        n_vehicles = len(vehicle_ids)
        if len(client_indices) < n_vehicles:
            raise ValueError("More vehicles than clients!")

        # Initialize clusters and vehicle loads using vehicle IDs
        routes = {vehicle_id: [] for vehicle_id in vehicle_ids}
        vehicle_loads = {vehicle_id: 0 for vehicle_id in vehicle_ids}
        vehicle_capacities = {vehicle_id: capacity for vehicle_id, capacity in zip(vehicle_ids, self.instance.fleet_df['Capacity'].tolist())}

        # Convert the full distance matrix to a condensed form required by linkage
        condensed_distance_matrix = squareform(self.instance.distance_matrix[client_indices][:, client_indices])

        # Perform hierarchical clustering
        Z = linkage(condensed_distance_matrix, 'ward')

        # Determine the number of routes based on the vehicle capacities
        routes_labels = fcluster(Z, n_vehicles, criterion='maxclust')

        # Map cluster labels to vehicle IDs
        label_to_vehicle_id = {label: vehicle_id for label, vehicle_id in zip(np.unique(routes_labels), vehicle_ids)}

        # Assign clients to routes based on labels
        for client_idx, label in zip(client_indices, routes_labels):
            client_demand = self.instance.nodes_df.at[client_idx, 'Items']
            vehicle_id = label_to_vehicle_id[label]

            if vehicle_loads[vehicle_id] + client_demand <= vehicle_capacities[vehicle_id]:
                routes[vehicle_id].append(client_idx)
                vehicle_loads[vehicle_id] += client_demand
            else:
                # If the vehicle is full, try to assign the client to another vehicle
                for other_vehicle_id in vehicle_ids:
                    if vehicle_loads[other_vehicle_id] + client_demand <= vehicle_capacities[other_vehicle_id]:
                        routes[other_vehicle_id].append(client_idx)
                        vehicle_loads[other_vehicle_id] += client_demand
                        break
                else:
                    # If no vehicle has enough capacity, raise an error
                    raise ValueError(f"No vehicle with enough capacity for client {client_idx}")

        # Convert route indices to client IDs
        for vehicle_id in routes:
            routes[vehicle_id] = [self.instance.nodes_df.at[idx, 'Id'] for idx in routes[vehicle_id]]
        return routes
    

    def initialize_routes_compact_kmeans(self):
        """
        Generate an initial feasible solution for the Vehicle Routing Problem using
        the K-Means clustering to create compact routes.
        """
        # Remove the depot node from the list of nodes to be clustered
        client_nodes = self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot']

        # Extract the location coordinates of the clients
        coordinates = client_nodes[['Latitude', 'Longitude']].values

        # Perform K-Means clustering to create compact clusters
        random_seed = np.random.randint(0, 10000)
        kmeans = KMeans(n_clusters=len(self.instance.fleet_df), random_state=random_seed).fit(coordinates)
        labels = kmeans.labels_

        # Initialize routes for each vehicle
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_capacities = {vehicle.Id: vehicle.Capacity for vehicle in self.instance.fleet_df.itertuples()}

        # Assign nodes to the nearest vehicle based on the clusters, respecting vehicle capacities
        for label, node in zip(labels, client_nodes.itertuples()):
            vehicle_id = self.instance.fleet_df.iloc[label]['Id']
            if vehicle_loads[vehicle_id] + node.Items <= vehicle_capacities[vehicle_id]:
                routes[vehicle_id].append(node.Id)
                vehicle_loads[vehicle_id] += node.Items
            else:
                # Find the closest vehicle that can take this node without exceeding capacity
                distances_to_vehicles = kmeans.transform([[node.Latitude, node.Longitude]])
                for idx in np.argsort(distances_to_vehicles[0]):
                    alt_vehicle_id = self.instance.fleet_df.iloc[idx]['Id']
                    if vehicle_loads[alt_vehicle_id] + node.Items <= vehicle_capacities[alt_vehicle_id]:
                        routes[alt_vehicle_id].append(node.Id)
                        vehicle_loads[alt_vehicle_id] += node.Items
                        break
        return routes
    

    def initialize_routes_heuristic_min_fleet_test(self):
        """
        Generate an initial feasible solution for the CVRP using a heuristic that
        selects a random unvisited node and assigns it to a vehicle's route based on
        certain conditions like capacity and compactness.
        """
        # Initialize configurations
        max_nodes = 45
        candidates_percentage = 5
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        routes_candidates = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        routes_centroids = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_capacities = {vehicle.Id: vehicle.Capacity for vehicle in self.instance.fleet_df.itertuples()}
        unvisited_nodes = set(self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot']['Id'])

        # Calculate node candidates based on candidates_percentage
        node_candidates = {}
        for node in self.instance.nodes_df.itertuples():
            if node.Node_Type != 'Depot':
                distances = self.instance.distance_matrix[node.Index]
                sorted_nodes = np.argsort(distances)
                num_candidates = int(len(sorted_nodes) * (candidates_percentage / 100))
                node_candidates[node.Id] = sorted_nodes[:num_candidates].tolist()

        # Initialize Vehicles with a random set of nodes
        previous_node = random.choice(list(unvisited_nodes))
        for vehicle in self.instance.fleet_df.itertuples():
            if not unvisited_nodes:
                break
            
            distances_to_previous_node = self.instance.distance_matrix[previous_node]
            adjusted_distances = np.where(np.isin(range(len(distances_to_previous_node)), list(unvisited_nodes), invert=True), 0, distances_to_previous_node)
            current_node = np.argmax(adjusted_distances)
            # current_node = random.choice(list(unvisited_nodes))

            # print("Creando ruta para el vehiculo: ", vehicle.Id)
            # If not exceed capacity and max nodesin route, we add it
            if vehicle_loads[vehicle.Id] + self.instance.nodes_df.at[current_node, 'Items'] <= vehicle.Capacity and len(routes[vehicle.Id]) <= max_nodes:
                routes[vehicle.Id].append(current_node)
                vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[current_node, 'Items']
                unvisited_nodes.remove(current_node)
                routes_candidates[vehicle.Id].extend(node_candidates[current_node])

                # Add Candidates
                stop = False
                while not stop:                   
                    min_distance = 1_000_000
                    best_candidate = None
                    best_candidate_items = None
                    previous_node = current_node
                    for candidate in routes_candidates[vehicle.Id]:
                        candidate_items = self.instance.nodes_df.at[candidate, 'Items']
                        if candidate in unvisited_nodes and vehicle_loads[vehicle.Id] + candidate_items <= vehicle_capacities[vehicle.Id]:
                            distance = self.instance.distance_matrix[candidate, previous_node]
                            if distance < min_distance:
                                min_distance = distance
                                best_candidate = candidate
                                best_candidate_items = candidate_items

                    if best_candidate is not None:
                        previous_node = best_candidate
                        routes[vehicle.Id].append(best_candidate)
                        vehicle_loads[vehicle.Id] += best_candidate_items
                        unvisited_nodes.remove(best_candidate)
                        routes_candidates[vehicle.Id].remove(best_candidate)
                        routes_candidates[vehicle.Id].extend(node_candidates[best_candidate])
                    else:
                        stop=True

        #print(node_candidates)
        return routes 
    

    def initialize_routes_heuristic_min_fleet(self):
        """
        Generate an initial feasible solution for the CVRP using a heuristic that
        selects a random unvisited node and assigns it to a vehicle's route based on
        certain conditions like capacity and compactness.
        """
        # Initialize configurations
        max_nodes = 45
        candidates_percentage = 5
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        routes_candidates = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        routes_centroids = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_capacities = {vehicle.Id: vehicle.Capacity for vehicle in self.instance.fleet_df.itertuples()}
        unvisited_nodes = set(self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot']['Id'])

        # Calculate node candidates based on candidates_percentage
        node_candidates = {}
        for node in self.instance.nodes_df.itertuples():
            if node.Node_Type != 'Depot':
                distances = self.instance.distance_matrix[node.Index]
                sorted_nodes = np.argsort(distances)
                num_candidates = int(len(sorted_nodes) * (candidates_percentage / 100))
                node_candidates[node.Id] = sorted_nodes[:num_candidates].tolist()

        # Initialize Vehicles with a random set of nodes
        for vehicle in self.instance.fleet_df.itertuples():
            if not unvisited_nodes:
                break
            current_node = random.choice(list(unvisited_nodes))
            # print("Creando ruta para el vehiculo: ", vehicle.Id)
            # If not exceed capacity and max nodesin route, we add it
            if vehicle_loads[vehicle.Id] + self.instance.nodes_df.at[current_node, 'Items'] <= vehicle.Capacity and len(routes[vehicle.Id]) <= max_nodes:
                routes[vehicle.Id].append(current_node)
                vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[current_node, 'Items']
                unvisited_nodes.remove(current_node)
                routes_candidates[vehicle.Id].extend(node_candidates[current_node])

                # Add Candidates
                stop = False
                while not stop:                   
                    min_distance = 1_000_000
                    best_candidate = None
                    best_candidate_items = None
                    previous_node = current_node
                    for candidate in routes_candidates[vehicle.Id]:
                        candidate_items = self.instance.nodes_df.at[candidate, 'Items']
                        if candidate in unvisited_nodes and vehicle_loads[vehicle.Id] + candidate_items <= vehicle_capacities[vehicle.Id]:
                            distance = self.instance.distance_matrix[candidate, previous_node]
                            if distance < min_distance:
                                min_distance = distance
                                best_candidate = candidate
                                best_candidate_items = candidate_items

                    if best_candidate is not None:
                        previous_node = best_candidate
                        routes[vehicle.Id].append(best_candidate)
                        vehicle_loads[vehicle.Id] += best_candidate_items
                        unvisited_nodes.remove(best_candidate)
                        routes_candidates[vehicle.Id].remove(best_candidate)
                        routes_candidates[vehicle.Id].extend(node_candidates[best_candidate])
                    else:
                        stop=True

        #print(node_candidates)
        return routes             

    def initialize_routes_heuristic(self):
        """
        Generate an initial feasible solution for the CVRP using a heuristic that
        selects a random unvisited node and assigns it to a vehicle's route based on
        certain conditions like capacity and compactness.
        """
        # Initialize configurations
        max_nodes = 45
        candidates_percentage = 5
        init_candidates = 3
        nodes_to_assing = 10
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_capacities = {vehicle.Id: vehicle.Capacity for vehicle in self.instance.fleet_df.itertuples()}
        unvisited_nodes = set(self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot']['Id'])

        # Calculate node candidates based on candidates_percentage
        node_candidates = {}
        for node in self.instance.nodes_df.itertuples():
            if node.Node_Type != 'Depot':
                distances = self.instance.distance_matrix[node.Index]
                sorted_nodes = np.argsort(distances)
                num_candidates = int(len(sorted_nodes) * (candidates_percentage / 100))
                node_candidates[node.Id] = sorted_nodes[:num_candidates].tolist()

        # Initialize Vehicles with a random set of nodes
        for vehicle in self.instance.fleet_df.itertuples():
            if not unvisited_nodes:
                break
            current_node = random.choice(list(unvisited_nodes))

            # If not exceed capacity and max nodesin route, we add it
            if vehicle_loads[vehicle.Id] + self.instance.nodes_df.at[current_node, 'Items'] <= vehicle.Capacity and len(routes[vehicle.Id]) <= max_nodes:
                routes[vehicle.Id].append(current_node)
                vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[current_node, 'Items']
                unvisited_nodes.remove(current_node)

                # Add Candidates
                for candidate in node_candidates[current_node]:
                    if candidate in unvisited_nodes:
                        if vehicle_loads[vehicle.Id] + self.instance.nodes_df.at[candidate, 'Items'] <= vehicle.Capacity and len(routes[vehicle.Id]) <= max_nodes:
                            routes[vehicle.Id].append(candidate)
                            vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[candidate, 'Items']
                            unvisited_nodes.remove(candidate)

                    if len(routes[vehicle.Id]) >= init_candidates:
                        break
        # print(routes)

        # Add route candidates
        routes_candidates = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        for vehicle, nodes in routes.items():
            # print('Vehiculo: ', vehicle, ' Nodos:', nodes)
            for node in nodes:
                candidates = node_candidates[node]
                for candidate in candidates:
                    if candidate in unvisited_nodes and not candidate in routes_candidates[vehicle]: # Add weight constraint?
                        routes_candidates[vehicle].append(candidate)
        # print(routes_candidates)

        # Solve problem by assigning nodes to vehicles
        #while unvisited_nodes:
        for i in range(nodes_to_assing):
            for vehicle, candidates in routes_candidates.items():
                route_nodes = routes[vehicle]
                # print('Ruta: ', vehicle, ' Nodos:', route_nodes,' Candidatos:', candidates)

                min_max_distance = float('inf')
                best_candidate = None
                for candidate in candidates:
                    if candidate in unvisited_nodes and self.instance.nodes_df.at[candidate, 'Items'] <= vehicle_capacities[vehicle]:
                        max_distance_to_route = max([self.instance.distance_matrix[candidate, route_node] for route_node in routes[vehicle]])
                        if max_distance_to_route < min_max_distance:
                            min_max_distance = max_distance_to_route
                            best_candidate = candidate

                if best_candidate is not None:
                    routes[vehicle].append(best_candidate)
                    vehicle_loads[vehicle] += self.instance.nodes_df.at[best_candidate, 'Items']
                    unvisited_nodes.remove(best_candidate)
                    routes_candidates[vehicle].remove(best_candidate)

        # print(routes_candidates)
        # print(routes)

        # Calculate Routes Centroids
        routes_centroid = {}
        for vehicle, nodes in routes.items():
            nodes_in_route_df = self.instance.nodes_df[self.instance.nodes_df['Id'].isin(nodes)]
            total_nodes = len(nodes_in_route_df)
            centroid_latitude = nodes_in_route_df['Latitude'].sum() / total_nodes
            centroid_longitude = nodes_in_route_df['Longitude'].sum() / total_nodes
            routes_centroid[vehicle] = (centroid_latitude, centroid_longitude)

        # print(routes_centroid)

        # Assign remaining nodes to routes
        for node in list(unvisited_nodes):
            # print("Insertando el nodo:", node)
            node_df = self.instance.nodes_df[self.instance.nodes_df['Id'] == node].iloc[0]
            items = node_df['Items']
            latitude = node_df['Latitude']
            longitude = node_df['Longitude']
            node_coords = (latitude, longitude)
            closest_routes_list = self.get_closest_routes_centroids(node_coords, routes_centroid) # Get a sorted list of the closest vehicles centroids from routes_centroid
            # print(closest_routes_list)

            for vehicle in closest_routes_list:
                route_nodes = routes[vehicle]
                route_total_nodes = len(route_nodes)
                route_load = vehicle_loads[vehicle]
                vehicle_capacicty = vehicle_capacities[vehicle]

                # We add the node
                if (route_load + items) <= vehicle_capacicty and (route_total_nodes + 1 <= max_nodes):
                    routes[vehicle].append(node)
                    vehicle_loads[vehicle] += items
                    unvisited_nodes.remove(node)
                    break

        return routes
    
    def get_closest_routes_centroids(self, node_coords, routes_centroid):
        """
        """
        distances_to_route = []
        distances_to_route_vehicles = []
        for vehicle, centroid in routes_centroid.items():
            distance = self.Geo.calculate_distance(node_coords, centroid)
            distances_to_route.append(distance)
            distances_to_route_vehicles.append(vehicle)

        # Combine the distances and vehicle IDs into a list of tuples and sort them by distance (ascending order)
        sorted_distances_with_vehicles = sorted(zip(distances_to_route, distances_to_route_vehicles), key=lambda x: x[0])

        # Extract the sorted vehicle IDs from the sorted list of tuples
        closest_routes_list = [vehicle for _, vehicle in sorted_distances_with_vehicles]

        return closest_routes_list


    def initialize_routes_heuristic2(self):
        """
        Generate an initial feasible solution for the CVRP using a heuristic that
        selects a random unvisited node and assigns it to a vehicle's route based on
        certain conditions like capacity and compactness.
        """
        # Initialize configurations
        max_nodes = 45
        candidates_percentage = 50
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        unvisited_nodes = set(self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot']['Id'])

        # Calculate node candidates based on candidates_percentage
        node_candidates = {}
        for node in self.instance.nodes_df.itertuples():
            if node.Node_Type != 'Depot':
                distances = self.instance.distance_matrix[node.Index]
                sorted_nodes = np.argsort(distances)
                num_candidates = int(len(sorted_nodes) * (candidates_percentage / 100))
                node_candidates[node.Id] = sorted_nodes[:num_candidates].tolist()

        # Solve problem by assigning nodes to vehicles
        while unvisited_nodes:
            for vehicle in self.instance.fleet_df.itertuples():
                if not unvisited_nodes:
                    break

                current_node = random.choice(list(unvisited_nodes))
                unvisited_nodes.remove(current_node)

                if vehicle_loads[vehicle.Id] + self.instance.nodes_df.at[current_node, 'Items'] <= vehicle.Capacity:
                    routes[vehicle.Id].append(current_node)
                    vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[current_node, 'Items']

                    if node_candidates[current_node]:
                        min_max_distance = float('inf')
                        best_candidate = None

                        for candidate in node_candidates[current_node]:
                            if candidate in unvisited_nodes:
                                max_distance_to_route = max([self.instance.distance_matrix[candidate, route_node] for route_node in routes[vehicle.Id]])
                                if max_distance_to_route < min_max_distance:
                                    min_max_distance = max_distance_to_route
                                    best_candidate = candidate

                        if best_candidate is not None:
                            routes[vehicle.Id].append(best_candidate)
                            vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[best_candidate, 'Items']
                            unvisited_nodes.remove(best_candidate)

        return routes
    
    ##################################################

    def initialize_routes_nearest_neighbor(self):
        """
        Generate an initial feasible solution for the CVRP using the Nearest Neighbor heuristic.
        """
        # Initialize clusters and vehicle loads and capacities using vehicle IDs
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_capacities = {vehicle.Id: vehicle.Capacity for vehicle in self.instance.fleet_df.itertuples()}
        depot_id = self.instance.nodes_df[self.instance.nodes_df['Name'] == 'Depot']['Id'].values[0]
        unvisited_nodes = set(self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot']['Id'])
        
        # Iterate over each vehicle to create a route
        for vehicle in self.instance.fleet_df.itertuples():
            if not unvisited_nodes:
                break  # Break the loop if there are no nodes left to visit

            # Start with the nearest node from the depot
            current_node = depot_id
            while unvisited_nodes and vehicle_loads[vehicle.Id] < vehicle.Capacity:
                nearest_next, min_dist = None, float('inf')
                for next_node in unvisited_nodes:
                    dist = self.instance.distance_matrix[current_node, next_node]
                    if dist < min_dist:
                        min_dist, nearest_next = dist, next_node
                
                if nearest_next is None:
                    break  # Break the loop if no nearest node was found

                next_node_items = self.instance.nodes_df.at[nearest_next, 'Items']
                if vehicle_loads[vehicle.Id] + next_node_items <= vehicle.Capacity:
                    routes[vehicle.Id].append(nearest_next)
                    vehicle_loads[vehicle.Id] += next_node_items
                    unvisited_nodes.remove(nearest_next)
                    current_node = nearest_next
                else:
                    break  # Break the loop if the node cannot be added due to capacity constraints

        # Check if all nodes have been assigned
        if unvisited_nodes:
            print(f"Warning: Not all nodes were assigned to a route. Unassigned nodes: {unvisited_nodes}")
            # Optionally, handle the unassigned nodes here
        return routes
    

    def initial_routes_compact(self):
        """
        Create initial routes with the objective of making them as compact as possible.
        """
        # Set of all nodes that have not been visited, excluding the depot
        depot_id = self.instance.nodes_df.iloc[0]['Id']
        unvisited_nodes = set(self.instance.nodes_df[self.instance.nodes_df['Node_Type'] != 'Depot'].index)
        
        # Initialize routes
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        vehicle_loads = {vehicle.Id: 0 for vehicle in self.instance.fleet_df.itertuples()}
        
        # Define a maximum distance threshold for compactness
        max_distance_threshold = 500.0  # Example threshold value, adjust as needed
        
        # Assign nodes to vehicles
        for vehicle in self.instance.fleet_df.itertuples():
            while unvisited_nodes and vehicle_loads[vehicle.Id] < vehicle.Capacity:
                if not routes[vehicle.Id]:  # If route is empty, start from depot
                    nearest_next, dist = self.find_nearest_neighbor(depot_id, unvisited_nodes)
                else:  # Otherwise, continue from last node in route
                    last_node = routes[vehicle.Id][-1]
                    nearest_next, dist = self.find_nearest_neighbor(last_node, unvisited_nodes)
                    
                # Check if the nearest node can be added without exceeding the capacity and distance threshold
                if nearest_next and vehicle_loads[vehicle.Id] + self.instance.nodes_df.at[nearest_next, 'Items'] <= vehicle.Capacity and dist <= max_distance_threshold:
                    routes[vehicle.Id].append(nearest_next)
                    vehicle_loads[vehicle.Id] += self.instance.nodes_df.at[nearest_next, 'Items']
                    unvisited_nodes.remove(nearest_next)
                else:
                    break  # If no suitable node is found, move to the next vehicle

        # Check if all nodes have been assigned
        if unvisited_nodes:
            print(f"Warning: Not all nodes were assigned to a route. Unassigned nodes: {unvisited_nodes}")
            # Handle unassigned nodes as needed
        return routes
    

    def find_nearest_neighbor(self, last_node, unvisited_clients):
        """
        Find the nearest neighbor to a given node from a set of unvisited clients.
        """
        nearest_next = None
        min_dist = float('inf')
        for client in unvisited_clients:
            dist = self.instance.distance_matrix[last_node][client]
            if dist < min_dist:
                min_dist = dist
                nearest_next = client
        return nearest_next, min_dist
    

    def initialize_routes_or_tools(self):
        """Solve the CVRP problem Using OR-Tools"""
        # Instantiate the data problem.
        data = {}
        data["distance_matrix"] = self.instance.distance_matrix
        data["demands"] = self.instance.nodes_df['Items'].tolist()  # Agregar los pesos de los nodos
        data["vehicle_capacities"] = self.instance.fleet_df['Capacity'].tolist()  # Capacidades de los vehículos
        data["num_vehicles"] = len(self.instance.fleet_df)
        data["depot"] = 0

        # Aquí, establece los puntos de inicio y fin de cada vehículo en el depósito.
        starts = [data["depot"]] * data["num_vehicles"]
        ends = [data["depot"]] * data["num_vehicles"]

        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], starts, ends)

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Capacity constraint.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
        search_parameters.time_limit.seconds = 45
        # search_parameters.time_limit.FromSeconds(1)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Extract solution and save it into routes
        routes = {vehicle.Id: [] for vehicle in self.instance.fleet_df.itertuples()}
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            # print('Ruta para el vehículo', vehicle_id + 1)
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != data["depot"]:
                    routes[vehicle_id + 1].append(node_index)
                index = solution.Value(routing.NextVar(index))

        return routes
        

    def create_routes_object(self, routes):
        """
        """
        # Add the depot at the start and end of each route
        depot_node = model.Node(self.parameters, self.instance, 0)
        initial_routes = list()   
        for vehicle_index in routes:
            if routes[vehicle_index]:                
                route = model.Route(self.parameters, self.instance, vehicle_index) # Create Route
                route.nodes.append(depot_node) # Add depot start                
                for node_id in routes[vehicle_index]: # Add nodes in route
                    current_node = model.Node(self.parameters, self.instance, node_id)
                    route.nodes.append(current_node)
                route.nodes.append(depot_node) # Add depot end

                route.fitness = route.calculate_route_distance(route.nodes)
                route.load = route.calculate_route_load()
                initial_routes.append(route)

        # Set routes
        self.routes = initial_routes
        

    def improve_single_route(self):
        """
        Apply routes improvements to each route created in initial solution
        """
        # print("Executing 2-opt, 3-opt...")
        solution_fitness = 0
        for route in self.routes:
            # print('Mejorando Ruta:', route.id, '... FITNESS:', route.fitness)

            route.two_opt() # Apply 2-opt to each route
            # print('\tFitness tras 2-opt:', route.id, '... FITNESS:', route.fitness)

            route.three_opt_first_improvement() # Apply 3-opt first improvent to each route
            # print('\tFitness tras 3-opt first improvement:', route.id, '... FITNESS:', route.fitness)

            route.three_opt() # Apply 3-opt to each route
            # print('\tFitness tras 3-opt:', route.id, '... FITNESS:', route.fitness)

            route.lin_kernighan(max_iter=10000, max_time_seconds=60) # Apply lin_kernighan to each route
            # print('\tFitness tras lin_kernighan:', route.id, '... FITNESS:', route.fitness)

            solution_fitness = solution_fitness + route.fitness
            # print('----------------------------------------------------------------')
        self.fitness = solution_fitness


    def improve_routes(self):
        i = 0

    def print_solution(self):
        for route in self.routes:
            print(route)

    def __str__(self) -> str:
        ind_str = 'Fitness: ' + str(self.fitness) + '\n'
        for route in self.routes:
            ind_str += str(route) + '\n'
        return ind_str