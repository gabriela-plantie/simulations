import numpy as np

from agents.orders import Order
from agents.riders import RiderStatus
from delivering import Dispatcher
from utils import OrderGenerator


def test_always_assigned_when_free_riders():
    # if orders not assigned -> no rider free
    # assert not riders free and orders not assigned

    num_riders = 5
    max_t = 5
    num_orders = 4
    orders = [
        Order(
            id=i,
            creation_at=0,
            restaurant_address=(i, i),
            customer_address=(i + 1, i + 1),
        )
        for i in range(num_orders)
    ]

    dispatcher = Dispatcher(
        bag_limit=1, dim=5, orders=orders, num_riders=num_riders, max_t=max_t
    )
    assert len(dispatcher.riders) == num_riders
    dispatcher.step()

    assert not (
        any([o.assigned_at is None for o in dispatcher.orders])
        and any([r.state == RiderStatus.RIDER_FREE for r in dispatcher.riders])
    )


def test_states():
    np.random.seed(19)
    num_riders = 1
    max_t = 10
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
    )
    dispatcher.step()
    assert (
        len(dispatcher.riders[0].queue) == 1
    ), "the rider should have an order assigned"
    assert (
        dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR
    ), "the state should be going to vendor"

    # check status change from going to vendor to going to customer
    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR:
        dispatcher.step()
    assert (
        len(dispatcher.riders[0].queue) == 0
    ), """When restarurant is reached
        and rider picking up from only one restaurant,
        queue should be empty"""  # TODO 2 asserts that go together
    assert (
        len(dispatcher.riders[0].bag) >= 1
    ), "when restarurant is reached, bag should have the orders"
    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
        dispatcher.step()
    assert len(dispatcher.riders[0].bag) == 0


def test_orders_times_steps():
    np.random.seed(19)
    num_riders = 1
    num_orders = 1
    max_t = 10

    orders = OrderGenerator(num_orders).create_orders(max_t)
    dispatcher = Dispatcher(
        bag_limit=1,
        dim=5,
        orders=orders,
        num_riders=num_riders,
        max_t=max_t,
    )
    assert all([o.assigned_at is None for o in dispatcher.orders])
    assert all([o.pick_up_at is None for o in dispatcher.orders])
    assert all([o.drop_off_at is None for o in dispatcher.orders])

    dispatcher.step()
    assert set([o.assigned_at for o in dispatcher.orders]) == {
        0,
        None,
    }

    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR:
        dispatcher.step()
    assert any([o.pick_up_at is not None for o in dispatcher.orders])

    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
        dispatcher.step()
    assert any([o.drop_off_at is not None for o in dispatcher.orders])


# stacking test
# creo 2 ordenes en t=0 en el mismo restaurant
# asigno las dos al mismo rider

# creo 2 ordenes en el mismo restaurant en t=1 y t=3
# neesito agregar un parametro de cuanto tiempo puede esperar en el restaurant
# las asigno a diferentes riders


def test_stacking():
    restaurant_address = (2, 4)
    num_riders = 2
    orders = [
        Order(
            id=i,
            creation_at=0,
            restaurant_address=restaurant_address,
            customer_address=cust_address,
        )
        for i, cust_address in enumerate([(2, 3), (3, 4)])
    ]
    dispatcher = Dispatcher(
        bag_limit=2,
        max_t=3,
        dim=5,
        orders=orders,
        num_riders=num_riders,
    )
    dispatcher.step()
    assert len(dispatcher.riders[0].queue) == 2

    # TODO add q en un momento tiene los dos en la bag
