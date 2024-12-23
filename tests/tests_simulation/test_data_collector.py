import math

import numpy as np

from simulate_delivering.agents.orders import Order
from simulate_delivering.agents.riders import Rider
from simulate_delivering.delivering import Dispatcher


def test_collector_no_stacking():
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
    riders = [
        Rider(id=i, shift_start_at=0, shift_end_at=5, starting_point=(0, 0))
        for i in range(num_riders)
    ]

    dispatcher = Dispatcher(
        bag_limit=1,
        max_t=max_t,
        dim=5,
        orders=orders,
        riders=riders,
    )

    for _ in range(max_t):
        dispatcher.step()

    assert all(
        [
            not (
                dispatcher.datacollector.model_vars["orders_waiting"][t] > 0
                and dispatcher.datacollector.model_vars["riders_idle"][t] > 0
            )
            for t in range(max_t)
        ]
    )
    # assert all(
    #     [
    #         (
    #             dispatcher.datacollector.model_vars["riders_before_shift"][t]
    #             + dispatcher.datacollector.model_vars["riders_idle"][t]
    #             + dispatcher.datacollector.model_vars["riders_going_to_vendor"][t]
    #             + dispatcher.datacollector.model_vars["riders_going_to_customer"][t]
    #             + dispatcher.datacollector.model_vars["riders_unavailable"][t]
    #         )
    #         == num_riders
    #         for t in range(max_t)
    #     ]
    # ), "in all steps total riders must be the same"
    # # TODO: change when incorporate rider start rider end

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
                dispatcher.datacollector.model_vars["orders_picked_up_cum"][t]
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
                dispatcher.datacollector.model_vars["orders_assigned_cum"][t]
                >= dispatcher.datacollector.model_vars["orders_picked_up_cum"][t]
                >= dispatcher.datacollector.model_vars["orders_delivered_cum"][t]
            )
            for t in range(max_t)
        ]
    ), """to be picked up orders should be assigned
      and to be delivered it has to be picked up"""


# TODO add test case for deliver time!


def test_collector_stacking():
    # must have at each t riders free, riders going to vendor, riders going to customer

    np.random.seed(19)
    num_riders = 2
    max_t = 30
    num_orders = 2

    orders = [
        Order(
            id=i,
            creation_at=0,
            restaurant_address=(3, 3),
            customer_address=(0, i * 2),
        )
        for i in range(num_orders)
    ]

    riders = [
        Rider(id=i, shift_start_at=0, shift_end_at=5, starting_point=(0, 0))
        for i in range(num_riders)
    ]
    dispatcher = Dispatcher(
        bag_limit=2,
        max_t=max_t,
        dim=10,
        orders=orders,
        riders=riders,
    )

    for _ in range(max_t):
        dispatcher.step()

    assert (
        max(
            list(
                filter(
                    lambda x: not math.isnan(x),
                    dispatcher.datacollector.model_vars["bag_size"],
                )
            )
        )
        == 2
    ), "Even though we have 2 riders, there should be stacking (bag size of 2)"
