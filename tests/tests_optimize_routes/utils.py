from simulate_delivering.optim_routes.utils import (
    Point,
    calculate_distances_dict,
    calculate_path_len,
    initialize_route_with_logic_from_restaurant,
)


def test_calculate_path_len():
    """
    ooooo
    o1ooo
    oo2oo
    o0ooo

    """

    sorted_orders = [
        Point(id=0, x=1, y=0),
        Point(id=2, x=2, y=1),
        Point(id=1, x=1, y=2),
    ]

    assert calculate_path_len(sorted_orders) == 4


def tests_calculate_distances_dict():
    points = [Point(id=0, x=1, y=0), Point(id=1, x=1, y=2), Point(id=2, x=2, y=1)]

    assert calculate_distances_dict(points) == {
        0: {1: 2, 2: 2},
        1: {0: 2, 2: 2},
        2: {0: 2, 1: 2},
    }


def test_initialize_route_with_logic():
    """
    Since this is only the first heuristic to create a route that is not
    completely random -> only the reduction of distance will be evaluated.

    Note the output here will not necessarily be optimal,
    since these algos are greedy, specially at this first step.

    1oooo
    ooooo
    o3ooo
    ooooo
    0ooo2

    """

    points = [
        Point(id=0, x=0, y=0),
        Point(id=1, x=0, y=4),
        Point(id=2, x=4, y=0),
        Point(id=3, x=1, y=2),
    ]

    distance_dict = calculate_distances_dict(points)
    total_distance, route = initialize_route_with_logic_from_restaurant(
        distance_dict, points
    )
    assert len(route) == len(points)
    assert total_distance < calculate_path_len(points)
