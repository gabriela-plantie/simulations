import pytest

from scripts.optim.tsp import XOpts
from scripts.optim.utils import Point, calculate_path_len


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

    assert [
        p.id for p in XOpts(route)._two_swap(route, *positions_to_swap)
    ] == expected_id_points


def test_sort_bag():
    """
    TSP sort of the bag.
    In the following graph:
    - S is the startiong point of the rider
    - R is restaurant
    - o is no customer
    - numbers represents orders and their positions are the correspondend
    customers places.
    o3ooo
    o20oo
    SR1oo
    ooooo
    ooooo
    """
    restaurant_point = Point(99, 1, 2)

    orders_in_bag = [Point(0, 2, 3), Point(1, 2, 2), Point(2, 1, 3), Point(3, 1, 4)]

    distance = calculate_path_len([restaurant_point] + orders_in_bag)
    # calculate_distances_dict([restaurant_point] + orders_in_bag)
    new_distance, new_route = XOpts(original_route=orders_in_bag).two_opt(
        current_position=restaurant_point
    )
    assert new_distance < distance
    assert [o.id for o in new_route] == [1, 0, 2, 3]
