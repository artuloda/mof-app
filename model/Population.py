from model import Individual
import random
class Population:

    def __init__(self, parameters, instance):
        self.parameters = parameters
        self.instance = instance
        self.individuals = list()
        self.individuals_fitness = list()
        self.best_individual = None
        self.best_fitness = 0

    def construct(self):
        """
        """
        # Creation
        options_names = {
            1: 'Hierarchical Clustering', 
            2: 'Compact Kmeans Clustering', 
            3: 'Random Assignment Heuristic', 
            4: 'Random Assignment Heuristic Minimize Fleet', 
            5: 'Nearest Neighborg Heuristic', 
            6: 'Routes Compact: Not stable', 
            7: 'CVRP Or-Tools'}
        print("Starting Algorithm...")
        print("Algorithm Options:", options_names)
        for iteration in range(self.parameters.TAM_POPULATION):
            # print('Start Iteration:', iteration, '...')
            individual = Individual(self.parameters, self.instance)
            if self.parameters.use_all_fleet == 'True':
                if iteration == 0:
                    option = 1
                else:
                    option = random.choice([2,3])
            else:
                if iteration == 0:
                    option = 7
                elif iteration == 1:
                    option = 5
                else:
                    option = 4
            individual.solve_cvrp(option)
            self.individuals.append(individual)
            self.individuals_fitness.append(individual.fitness)
            print('End Iteration:', iteration, ' Algorithm Option:', option, ' - ', options_names[option], ' FITNESS:', individual.fitness)

        # Evaluation
        best_solution_index = self.individuals_fitness.index(min(self.individuals_fitness))
        self.best_individual = self.individuals[best_solution_index]
        self.best_fitness = self.individuals_fitness[best_solution_index]

    def __str__(self) -> str:
        print('Population:', self.individuals, ' BEST SOLUTION:', self.best_individual.fitness)