import random

import pytest

from simulate_delivering.agents.orders import Order
from simulate_delivering.agents.riders import Rider
from simulate_delivering.delivering import Dispatcher
from simulate_delivering.optim_routes.tsp import LocalSearch
from simulate_delivering.optim_routes.utils import Point, calculate_path_len, two_swap


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
    new_distance, new_route = LocalSearch(
        current_position=restaurant_point, original_route=orders_in_bag
    ).search()
    assert new_distance < distance
    assert new_distance == expected_distance
    assert [o.id for o in new_route][1:] == expected_route_ids


def test_vrp_assign_vendor_to_rider():
    """
    MIP to choose for each rider the vendor that
    min the total distances from where riders are to vendors.
    In the following graph:
    - vi is vendor
    - r is a rider
    - o is no customer
    - numbers represents orders and their positions are the correspondend
    customers places.
    """

    # o   o   o   o   v2
    # o   o   o   o   o
    # o   o   o   o   o
    # v1  o   o   o   o
    # o  r2   r1  o   o

    orders = [
        Order(
            id=1,
            creation_at=0,  # (i+1)*1,
            restaurant_address=(0, 1),
            customer_address=(3, 0),
        ),
        Order(
            id=2,
            creation_at=0,  # (i+1)*1,
            restaurant_address=(4, 4),
            customer_address=(3, 1),
        ),
    ]

    riders = [
        Rider(id=1, shift_start_at=0, shift_end_at=5, starting_point=(2, 0)),
        Rider(id=2, shift_start_at=0, shift_end_at=5, starting_point=(1, 0)),
    ]

    dispatcher_config = {
        "bag_limit": 3,
        "max_t": 10,
        "dim": 4,
        "orders": orders,
        "riders": riders,
    }
    dispatcher = Dispatcher(**dispatcher_config)
    dispatcher.step()
    assert [(r.id, o.id) for r in dispatcher.riders for o in r._queue] == [
        (1, 2),
        (2, 1),
    ], "order should be assigned to rider closer to vendor"

    assert [r.pos for r in dispatcher.riders if r.id == 2][0] == (
        0,
        0,
    ), "rider 2 moved to position 0,0"

    # o     o      o    o   O2v2
    # o     o      o    o   o
    # o     O3v2   o    o   o
    # O1v1   o     o    o   o
    # o     r2     r1   o   o

    orders.append(
        Order(
            id=3,
            creation_at=1,  # (i+1)*1,
            restaurant_address=(4, 4),
            customer_address=(1, 2),
        )
    )
    dispatcher = Dispatcher(**dispatcher_config)

    dispatcher.step()  # t=0
    assert [(r.id, o.id) for r in dispatcher.riders for o in r._queue] == [
        (1, 2),
        (2, 1),
    ], "order should be assigned to rider closer to vendor"

    assert [r.pos for r in dispatcher.riders if r.id == 2][0] == (
        0,
        0,
    ), "rider 2 moved to position 0,0"

    dispatcher.step()  # t=1
    assert [(r.id, o.id) for r in dispatcher.riders for o in r._queue] == [
        (1, 2),
        (1, 3),
        (2, 1),
    ], "order should be assigned to rider already going to vendor"

    assert [r.pos for r in dispatcher.riders if r.id == 2][0] == (
        0,
        1,
    ), "rider 2 moved to position 0,1"
