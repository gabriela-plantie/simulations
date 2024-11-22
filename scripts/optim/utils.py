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
