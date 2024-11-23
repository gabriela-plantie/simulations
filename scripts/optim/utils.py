# from collections import namedtuple


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


def preprocess_bag(orders):
    orders_points = []
    for o in orders:
        x, y = o.customer_address
        id = o.id
        orders_points.append(Point(id, x, y))
    return orders_points


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


def initialize_route_with_logic(distance_dict, route):
    """
    Nearest neighbor algorithm to set up coherent path.
    """
    unvisited = route.copy()
    current_position = route[0]
    route = [current_position]
    unvisited.remove(current_position)
    total_d = 0  # total distance

    while len(unvisited) > 0:
        # choose city with the lowest edge weight
        min_distance = 9999999  # minimum distance to nearest city
        for point in unvisited:  # for each city
            [min_point, max_point] = sorted(
                [current_position, point], key=lambda p: p.id
            )
            # sorted([current_position, point])
            distance = distance_dict[min_point.id][max_point.id]
            if distance < min_distance:
                min_distance = distance
                next_point = point

        total_d += min_distance  # update total distance
        current_position = next_point  # move to next city
        route += [current_position]  # add city to tour
        unvisited.remove(current_position)  # mark visited

    # # Distance to return
    # [min_point_num, max_point_num] = sorted([route[0], route[len(route) - 1]])
    # total_d += distance_dict[min_point_num][max_point_num]
    return total_d, route  # tour distance is [0], since number of cities varies
