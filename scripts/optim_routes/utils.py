import numpy as np

from scripts.agents.orders import Order


class Point:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.id == other.id and self.x == other.x and self.y == other.y
        return False


# Point = namedtuple("Point", ["id", "x", "y"])


def length(point1, point2):
    return abs(point1.x - point2.x) + abs(point1.y - point2.y)


def orders_to_points(orders: list[Order]):
    orders_points = []
    for o in orders:
        x, y = o.customer_address
        id = o.id
        orders_points.append(Point(id, x, y))
    return orders_points


def points_to_orders(points: list[Point], orders: list[Order]):
    sorted_orders = []
    for p in points:
        sorted_orders.extend([o for o in orders if o.id == p.id])
    return sorted_orders


def calculate_path_len(points: list[Point], path_type: str = "open"):

    node_count = len(points)
    distance = 0

    if path_type == "closed":
        raise TypeError("closed path not implemented")
        # distance = length(points[-1], points[0]) # for closed path

    for i in range(0, node_count - 1):
        distance += length(points[i], points[i + 1])

    return distance


def calculate_distances_dict(points: list[Point]):
    """
    Used only for:
     - VRP (all points)
     - TSP (only with the elements already in the bag)
    """
    # for now I will do a symmetric matrix
    # TODO see how to do triangular
    # with no need of sorting by accessing the id of the point
    distances_dict = {}
    for p1 in points:
        distances_dict[p1.id] = {}
        for p2 in points:
            if p1 != p2:
                distances_dict[p1.id][p2.id] = length(p1, p2)
    return distances_dict


def initialize_route_with_logic_from_restaurant(
    distance_dict: dict, route_with_restaurant: list[Point]
):
    """
    Nearest neighbor algorithm to set up coherent path.
    Since for sorting the bag I have to start from the restaurant,
    I am fixing the first position there.
    """
    unvisited = route_with_restaurant.copy()
    current_position = route_with_restaurant[0]
    route_with_restaurant = [current_position]
    unvisited.remove(current_position)
    total_d = 0  # total distance

    while len(unvisited) > 0:
        # choose city with the lowest edge weight
        min_distance = 9999999  # minimum distance to nearest city
        for point in unvisited:  # for each city

            # sorted([current_position, point])
            distance = distance_dict[current_position.id][point.id]
            if distance < min_distance:
                min_distance = distance
                next_point = point

        total_d += min_distance  # update total distance
        current_position = next_point  # move to next city
        route_with_restaurant += [current_position]  # add city to tour
        unvisited.remove(current_position)  # mark visited

    # # Distance to return
    # [min_point_num, max_point_num] = sorted([route[0], route[len(route) - 1]])
    # total_d += distance_dict[min_point_num][max_point_num]
    return (
        total_d,
        route_with_restaurant,
    )  # tour distance is [0], since number of cities varies


def two_swap(route: list[Point], i: int, j: int):
    """
    - i and j are positions.
    - j > i
    - if it takes a route that crosses over itself -> untangles it
    """
    # assert i<j
    if j < (len(route) - 1):
        route = route[:i] + list(np.flipud(route[i : j + 1])) + route[j + 1 :]
    else:
        # if j == len(route)
        route = route[:i] + list(np.flipud(route[i:]))
    #  assert len(path) == len(set(path))
    #  assert set(route) == set(path)
    return route
