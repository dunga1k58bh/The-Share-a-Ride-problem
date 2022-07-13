from ortools.linear_solver import pywraplp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import time

"""Simple Pickup Delivery Problem (PDP)."""


def create_data_model():
    """Get data from file"""
    tmp = []
    with open("./res/data.text", "r") as f:
        for i in f.readlines():
            i = i.replace("\n", "")
            i = i.rstrip(" ").split(" ")
            tmp.append([int(j) for j in i])
    f.close()

    distanceMatrix = tmp[3:]
    hanhkhach = tmp[0][0]
    goihang = tmp[0][1]
    vehicleNumber = tmp[0][2]
    khoiLuongGoiHang = tmp[1]
    khoiLuongToiDaMoiXe = tmp[2]
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distanceMatrix
    data['pickups_deliveries'] = [
        [i, i+hanhkhach+goihang] for i in range(1, hanhkhach+goihang+1)
    ]
    data['demands'] = [0 for i in range(hanhkhach+1)] + khoiLuongGoiHang + [
        0 for i in range(hanhkhach)] + list(map(lambda x: -x, khoiLuongGoiHang))
    data['passengers'] = [0] + [1 for i in range(hanhkhach)] + [0 for i in range(
        goihang)] + [-1 for i in range(hanhkhach)] + [0 for i in range(goihang)]
    data['vehicle_capacities'] = khoiLuongToiDaMoiXe
    data['passenger_capacities'] = [1 for i in range(vehicleNumber)]
    data['num_vehicles'] = vehicleNumber
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
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
            # plan_output += ' {0} Load({1} and {2}) -> '.format(node_index, route_load, pack_load)
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


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

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
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1 ** 3)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


if __name__ == "__main__":
    rt = time.time()
    main()
    st = time.time()
    print(f"Time running: {st - rt}")
