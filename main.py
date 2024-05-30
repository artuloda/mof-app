import algorithm
import time


if __name__ == '__main__':
    start_time = time.time()
    # random_seed = 123456789
    # np.random.seed(random_seed)

    # Read Parameters
    parameters = algorithm.Parameters()
    print(parameters)

    # Create Instance
    # instance = algorithm.Instance(parameters)
    # print(instance.nodes_df)
    # print(instance.fleet_df)

    # solution = algorithm.Solution(parameters, instance)
    # solution.save_solution()    
    # print(solution.best_solution)
    # print('Best FITNESS:', solution.fitness)

    # validation = algorithm.Validation(parameters, instance, solution)
    # validation.validate()
    
    # map_object = algorithm.Map(parameters, instance, solution)
    # map_object.draw_map()

    end_time = time.time()
    print("Total Execution Time: " + str(round(end_time - start_time, 2)) + "s")
    

def main():
    start_time = time.time()
    # random_seed = 123456789
    # np.random.seed(random_seed)

    # Read Parameters
    parameters = algorithm.Parameters()
    print(parameters)

    # Create Instance
    instance = algorithm.Instance(parameters)
    # print(instance.nodes_df)
    # print(instance.fleet_df)

    solution = algorithm.Solution(parameters, instance)
    solution.save_solution()    
    print(solution.best_solution)
    print('Best FITNESS:', solution.fitness)

    validation = algorithm.Validation(parameters, instance, solution)
    validation.validate()
    
    map_object = algorithm.Map(parameters, instance, solution)
    map_object.draw_map()

    end_time = time.time()
    print("Total Execution Time: " + str(round(end_time - start_time, 2)) + "s")

    return instance.nodes_df, instance.fleet_df, solution.result_df, solution.result_graph_json