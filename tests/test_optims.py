import random

import pytest

from scripts.optim.tsp import XOpts
from scripts.optim.utils import Point, calculate_path_len, two_swap


@pytest.mark.parametrize(
    "positions_to_swap, expected_id_points",
    [
        ([1, 3], [1, 3, 2, 0, 4, 5]),
        ([1, 4], [1, 4, 3, 2, 0, 5]),
        ([1, 5], [1, 5, 4, 3, 2, 0]),
    ],
)
def test_two_swap(positions_to_swap, expected_id_points):
    route = [
        Point(1, 1, 2),
        Point(0, 0, 1),
        Point(2, 2, 3),
        Point(3, 3, 4),
        Point(4, 4, 5),
        Point(5, 5, 6),
    ]

    assert [p.id for p in two_swap(route, *positions_to_swap)] == expected_id_points


@pytest.mark.parametrize(
    "restaurant, orders_positions, expected_route_ids, expected_distance",
    [
        ((1, 2), [(2, 3), (2, 2), (1, 3), (1, 4)], [1, 0, 2, 3], 4),
        # o3ooo
        # o20oo
        # oR1oo
        # ooooo
        # ooooo
        ((1, 2), [(2, 3), (2, 2), (1, 3), (1, 4), (1, 1)], [4, 1, 0, 2, 3], 6),
        # o3ooo
        # o20oo
        # oR1oo
        # o4ooo
        # ooooo
    ],
)
def test_2opt_for_bag(
    restaurant, orders_positions, expected_route_ids, expected_distance
):
    """
    TSP sort of the bag.
    In the following graph:
    - R is restaurant
    - o is no customer
    - numbers represents orders and their positions are the correspondend
    customers places.
    """
    random.seed(1)
    restaurant_point = Point(99, *restaurant)

    orders_in_bag = [Point(i, p[0], p[1]) for i, p in enumerate(orders_positions)]

    distance = calculate_path_len([restaurant_point] + orders_in_bag)
    # calculate_distances_dict([restaurant_point] + orders_in_bag)
    new_distance, new_route = XOpts(
        current_position=restaurant_point, original_route=orders_in_bag
    ).local_search()
    assert new_distance < distance
    assert new_distance == expected_distance
    assert [o.id for o in new_route][1:] == expected_route_ids
