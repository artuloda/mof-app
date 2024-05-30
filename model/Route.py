import model

import time

class Route:

    def __init__(self, parameters, instance, id):
        self.parameters = parameters
        self.instance = instance
        self.id = id
        self.nodes = list()
        self.load = 0
        self.vehicle = None
        self.fitness = 100_000_000
        self.set_vehicle()


    def set_vehicle(self):
        """
        """
        self.vehicle = model.Vehicle(self.parameters, self.instance, self.id)


    # Function to calculate the total load of a route
    def calculate_route_load(self):
        total_load = 0
        for node in self.nodes:
            total_load += node.items
        return total_load


    # Function to calculate the total distance of a route
    def calculate_route_distance(self, route=None):
        if route is None:
            route = self.nodes
        return sum(self.instance.distance_matrix[route[i].id, route[i+1].id] for i in range(len(route)-1))
        

    # Functions to apply 2-opt optimization on a single route
    def two_opt(self):
        improved = True
        while improved:
            improved = False
            for i in range(1, len(self.nodes) - 2):
                for j in range(i + 1, len(self.nodes) - 1):
                    new_route = self.nodes[:i] + self.nodes[i:j+1][::-1] + self.nodes[j+1:]
                    new_distance = self.calculate_route_distance(new_route)
                    if new_distance < self.fitness:
                        self.nodes = new_route
                        self.fitness = new_distance
                        improved = True


    # Functions to apply 3-opt optimization on a single route
    def three_opt(self):
        """Applies 3-opt optimization on the given route."""
        improvement = True
        while improvement:
            improvement = False
            for i in range(1, len(self.nodes) - 2):
                for j in range(i + 1, len(self.nodes) - 1):
                    for k in range(j + 2, len(self.nodes) + (i > 0)):
                        delta = self.reverse_segment_if_better(i, j, k)
                        if delta < 0:
                            improvement = True
                            self.fitness += delta


    def reverse_segment_if_better(self, i, j, k):
        """Reverses segment if it improves the total distance."""
        # Adjust indices for 0-based indexing and get nodes
        A, B, C, D, E, F = self.nodes[i-1], self.nodes[i], self.nodes[j-1], self.nodes[j], self.nodes[k-1], self.nodes[k % len(self.nodes)]
        distance_matrix = self.instance.distance_matrix
        d0 = distance_matrix[A.id, B.id] + distance_matrix[C.id, D.id] + distance_matrix[E.id, F.id]
        d1 = distance_matrix[A.id, C.id] + distance_matrix[B.id, D.id] + distance_matrix[E.id, F.id]
        d2 = distance_matrix[A.id, B.id] + distance_matrix[C.id, E.id] + distance_matrix[D.id, F.id]
        d3 = distance_matrix[A.id, D.id] + distance_matrix[E.id, B.id] + distance_matrix[C.id, F.id]
        d4 = distance_matrix[F.id, B.id] + distance_matrix[C.id, D.id] + distance_matrix[E.id, A.id]

        if d0 > d1:
            self.nodes[i:j] = reversed(self.nodes[i:j])
            return -d0 + d1
        elif d0 > d2:
            self.nodes[j:k] = reversed(self.nodes[j:k])
            return -d0 + d2
        elif d0 > d4:
            self.nodes[i:k] = reversed(self.nodes[i:k])
            return -d0 + d4
        elif d0 > d3:
            tmp = self.nodes[j:k] + self.nodes[i:j]
            self.nodes[i:k] = tmp
            return -d0 + d3
        return 0


    # Functions to apply 3-opt in fisrt improvement
    def three_opt_first_improvement(self, max_segment_length=10):
        """Applies a limited 3-opt search that looks for the first improvement."""
        length = len(self.nodes)
        improved = True
        while improved:
            improved = False
            for i in range(1, length - 2):
                for j in range(i + 1, min(i + max_segment_length, length - 1)):
                    for k in range(j + 1, min(j + max_segment_length, length)):
                        # Save the current state to compare after potential improvements
                        before_change = self.fitness
                        # Try reversing the segments and see if it improves the route
                        self.reverse_segment_if_improves(i, j)
                        self.reverse_segment_if_improves(j, k)

                        # Recalculate fitness after the changes
                        after_change = self.calculate_route_distance()

                        # Check if there was an improvement
                        if after_change < before_change:
                            self.fitness = after_change  # Update the fitness with the improved distance
                            improved = True
                            break  # Exit the innermost loop on the first improvement
                        else:
                            # Revert changes if no improvement
                            self.reverse_segment_if_improves(j, k)  # Revert previous reversal
                            self.reverse_segment_if_improves(i, j)  # Revert first reversal
                    if improved:
                        break  # Break the second loop if improved
                if improved:
                    break  # Break the outer loop if improved


    def reverse_segment_if_improves(self, start, end):
        """Reverses the segment in the route if it results in an improvement."""
        self.nodes[start:end] = self.nodes[start:end][::-1]


    def lin_kernighan(self, max_iter, max_time_seconds):              
        start_time = time.time() # Record the start time of the algorithm to enforce a time limit
        
        # Initialize the improvement flag and iteration counter
        improved = True
        total_iterations = 0
        # Continue optimizing until no improvement is found, the max number of iterations is reached, or the max time allowed is exceeded
        while improved and total_iterations < max_iter and (time.time() - start_time) < max_time_seconds:                                
            improved = False  # Reset the improvement flag for this iteration

            # Iterate over all pairs of nodes within the route, except for the first and last edges
            for i in range(1, len(self.nodes) - 2):
                for j in range(i + 1, len(self.nodes) - 1):
                    
                    # If the maximum time allowed for the algorithm has been exceeded, terminate and return
                    if (time.time() - start_time) > max_time_seconds:
                        print("Max time reached")
                        return

                    # Create a new route by reversing the segment between nodes i and j
                    new_route = self.nodes[:i] + self.nodes[i:j+1][::-1] + self.nodes[j+1:]
                    
                    # If the new route has a shorter distance than the current route, update the route and its fitness
                    if self.calculate_route_distance(new_route) < self.calculate_route_distance():
                        self.nodes = new_route
                        self.fitness = self.calculate_route_distance()
                        improved = True  # Set the improvement flag
                        break  # Break out of the inner loop early due to improvement

                # If an improvement was found, break out of the second loop early
                if improved:
                    break

            # Increment the total number of iterations after each complete pass through the route
            total_iterations += 1


    def __str__(self) -> str:
        route_str = 'Vehicle: ' +  str(self.vehicle.name) + ' Fitness: ' +  str(self.fitness) + ' Load: ' +  str(self.load) + ' Total Nodes: ' +  str(len(self.nodes) - 2) + ' ---> '
        for node in self.nodes:
            route_str += str(node.id) + '-'
        return route_str[:-1]