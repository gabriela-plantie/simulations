# import pytest

from scripts.agents.orders import Order
from scripts.agents.riders import Rider
from scripts.delivering import Dispatcher


def test_sort_bag():
    """
    TSP sort of the bag.
    In the following graph:
    - S is the startiong point of the rider
    - R is restaurant
    - o is no customer
    - numbers represents orders and their positions are the correspondend
    customers places.

    # o3ooo
    # o20oo
    # oR1oo
    # ooooo
    # ooooo
    """
    sp = (1, 3)
    rider = [Rider(id=1, shift_start_at=0, shift_end_at=10, starting_point=sp)]
    orders = [
        Order(
            id=i,
            creation_at=i,
            restaurant_address=(2, 3),
            customer_address=customer_address,
            preparation_time=0,
        )
        for i, customer_address in enumerate([(3, 4), (3, 3), (2, 4), (2, 5)])
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
