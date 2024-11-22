# import pytest

from scripts.agents.orders import Order
from scripts.agents.riders import Rider
from scripts.delivering import Dispatcher
from scripts.optim.tsp import XOpts
from scripts.optim.utils import Point


def test_two_swap():
    route = [
        Point(1, 1, 2),
        Point(0, 0, 1),
        Point(2, 2, 3),
        Point(3, 3, 4),
        Point(4, 4, 5),
    ]

    assert XOpts(route)._two_swap(route, 1, 3) == [
        Point(1, 1, 2),
        Point(0, 0, 1),
        Point(3, 3, 4),
        Point(2, 2, 3),
        Point(4, 4, 5),
    ]


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
    sp = (0, 2)
    rider = [Rider(id=1, shift_start_at=0, shift_end_at=10, starting_point=sp)]
    orders = [
        Order(
            id=i,
            creation_at=i,
            restaurant_address=(1, 2),
            customer_address=customer_address,
            preparation_time=0,
        )
        for i, customer_address in enumerate(
            [(2, 3), (2, 2), (1, 3), (1, 4)]  # 0  # 1  # 2  # 3
        )
    ]

    dispatcher = Dispatcher(
        bag_limit=4,
        max_t=20,
        dim=5,
        orders=orders,
        riders=rider,
    )

    for _ in range(20):
        dispatcher.step()

    assert [o.i for o in dispatcher.orders] == [1, 0, 2, 3]
