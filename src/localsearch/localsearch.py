from ortools.linear_solver import pywraplp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import time


def create_data_model(i):
    """Get data from file"""
    tmp = []
    with open(f"./res/testcase1/test{i}.txt", "r") as f:
        for i in f.readlines():
            i = i.replace("\n", "")
            i = i.rstrip(" ").split(" ")
            tmp.append([int(j) for j in i])
    f.close()

    distanceMatrix = tmp[3:]
    passengerNumber = tmp[0][0]
    parcelNumber = tmp[0][1]
    vehicleNumber = tmp[0][2]
    parcelWeight = tmp[1]
    maxWeightVehicle = tmp[2]
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distanceMatrix
    # pickup at i and delivery at i + N + M
    data['pickups_deliveries'] = [
        [i, i+passengerNumber+parcelNumber] for i in range(1, passengerNumber+parcelNumber+1)
    ]
    # pickup and delivery parcel
    data['demands'] = [0 for i in range(passengerNumber+1)] + parcelWeight + [
        0 for i in range(passengerNumber)] + list(map(lambda x: -x, parcelWeight))
    # pickup and delivery passengers
    data['passengers'] = [0] + [1 for i in range(passengerNumber)] + [0 for i in range(
        parcelNumber)] + [-1 for i in range(passengerNumber)] + [0 for i in range(parcelNumber)]

    data['vehicle_capacities'] = maxWeightVehicle
    data['passenger_capacities'] = [1 for i in range(vehicleNumber)]
    data['num_vehicles'] = vehicleNumber
    # 0 -> ... -> 0
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution, i):
    """Prints solution on console."""
    print(f'Test: {i}')
    output_distance = 0

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_load = 0
        pack_load = 0
        plan_output = 'Car {}: '.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['passengers'][node_index]
            pack_load += data['demands'][node_index]
            plan_output += ' {0} -> '.format(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}\n'.format(route_distance)
        print(plan_output)
        output_distance = max(output_distance, route_distance)
    print('Maximum of all routes: {}'.format(output_distance))


def main(i):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(i)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Add Passenger constraint.
    def demand_passenger_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['passengers'][from_node]
    demand_passenger_callback_index = routing.RegisterUnaryTransitCallback(
        demand_passenger_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_passenger_callback_index,
        0,  # null capacity slack
        data['passenger_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Passenger Capacity')

    # Define Transportation Requests.
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_index) <=
            distance_dimension.CumulVar(delivery_index))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    # search_parameters.local_search_metaheuristic = (
    #     routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    # search_parameters.local_search_metaheuristic = (
    #     routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING)
    # search_parameters.local_search_metaheuristic = (
    #     routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)
    search_parameters.time_limit.FromSeconds(600)

    # Solve the problem.
    
    rt = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    st = time.time()

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution, i)
        print(f"Time running: {st - rt}")
    else:
        print("NOOOOO")


if __name__ == "__main__":
    for i in range(1, 2):
        main(i)
