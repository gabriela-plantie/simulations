import numpy as np

from agents.orders import Order
from delivering import Dispatcher


def test_collector():
    # must have at each t riders free, riders going to vendor, riders going to customer

    np.random.seed(19)
    num_riders = 1
    max_t = 20
    num_orders = 2

    orders = [
        Order(
            id=i,
            creation_at=0,
            restaurant_address=(i, i),
            customer_address=(i + 1, i),
        )
        for i in range(num_orders)
    ]

    dispatcher = Dispatcher(
        bag_limit=1,
        max_t=max_t,
        dim=5,
        orders=orders,
        num_riders=num_riders,
        starting_point=(0, 0),
    )

    for _ in range(max_t):
        dispatcher.step()

    assert all(
        [
            (
                dispatcher.datacollector.model_vars["riders_free"][t]
                + dispatcher.datacollector.model_vars["riders_going_to_vendor"][t]
                + dispatcher.datacollector.model_vars["riders_going_to_customer"][t]
            )
            == num_riders
            for t in range(max_t)
        ]
    ), "in all steps total riders must be the same"
    # TODO: change when incorporate rider start rider end

    assert (
        max(
            [
                dispatcher.datacollector.model_vars["orders_assigned"][t]
                for t in range(max_t)
            ]
        )
        <= num_orders
    ), "assigned orders must have been less or equal to total orders"

    assert (
        max(
            [
                dispatcher.datacollector.model_vars["orders_picked_up"][t]
                for t in range(max_t)
            ]
        )
        <= num_orders
    ), "picked up orders must have been less or equal to total orders"

    assert (
        max(
            [
                dispatcher.datacollector.model_vars["orders_delivered"][t]
                for t in range(max_t)
            ]
        )
        <= num_orders
    ), "delivered orders must have been less or equal to total orders"

    assert all(
        [
            (
                dispatcher.datacollector.model_vars["orders_assigned"][t]
                >= dispatcher.datacollector.model_vars["orders_picked_up"][t]
                >= dispatcher.datacollector.model_vars["orders_delivered"][t]
            )
            for t in range(max_t)
        ]
    ), """to be picked up orders should be assigned
      and to be delivered it has to be picked up"""


# TODO add test case for deliver time!
