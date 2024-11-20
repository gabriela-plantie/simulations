import numpy as np
import pytest

from agents.orders import Order
from agents.riders import Rider, RiderStatus
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
    riders = [
        Rider(id=1, shift_start_at=0, shift_end_at=5, starting_point=(0, 0))
        for _ in range(num_riders)
    ]

    dispatcher = Dispatcher(
        bag_limit=1, dim=5, orders=orders, riders=riders, max_t=max_t
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
            restaurant_address=(i + 1, i),
            customer_address=(i + 1, i),
        )
        for i in range(num_orders)
    ]

    riders = [
        Rider(id=1, shift_start_at=0, shift_end_at=5, starting_point=(0, 0))
        for _ in range(num_riders)
    ]

    dispatcher = Dispatcher(
        bag_limit=1,
        max_t=max_t,
        dim=5,
        orders=orders,
        riders=riders,
    )
    dispatcher.step()
    assert (
        len(dispatcher.riders[0]._queue) == 1
    ), "the rider should have an order assigned"
    assert (
        dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR
    ), "the state should be going to vendor"

    # check status change from going to vendor to going to customer
    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR:
        dispatcher.step()
    assert (
        len(dispatcher.riders[0]._queue) == 0
    ), """When restarurant is reached
        and rider picking up from only one restaurant,
        queue should be empty"""  # TODO 2 asserts that go together
    assert (
        len(dispatcher.riders[0]._bag) >= 1
    ), "when restarurant is reached, bag should have the orders"
    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
        dispatcher.step()
    assert len(dispatcher.riders[0]._bag) == 0


def test_orders_times_steps():
    np.random.seed(19)
    num_riders = 1
    num_orders = 1
    max_t = 10

    orders = OrderGenerator(num_orders).create_orders(max_t)
    riders = [
        Rider(id=1, shift_start_at=0, shift_end_at=5, starting_point=(0, 0))
        for _ in range(num_riders)
    ]
    dispatcher = Dispatcher(
        bag_limit=1,
        dim=5,
        orders=orders,
        riders=riders,
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
    restaurant_address = (1, 1)
    num_riders = 2
    orders = [
        Order(
            id=i,
            creation_at=0,
            restaurant_address=restaurant_address,
            customer_address=cust_address,
        )
        for i, cust_address in enumerate([(2, 2), (2, 3)])
    ]
    riders = [
        Rider(id=1, shift_start_at=0, shift_end_at=5, starting_point=(0, 0))
        for _ in range(num_riders)
    ]
    dispatcher = Dispatcher(
        bag_limit=2,
        max_t=5,
        dim=5,
        orders=orders,
        riders=riders,
    )
    dispatcher.step()
    assert len(dispatcher.riders[0]._queue) == 2
    dispatcher.step()
    dispatcher.step()
    assert len(dispatcher.riders[0]._queue) == 0
    assert len(dispatcher.riders[0]._bag) == 2

    # TODO fix pick up -> bag creation
    # should move all orders in queue to bag at once if restaurant is the same
    # TODO add q en un momento tiene los dos en la bag


@pytest.mark.parametrize(
    "creation_at, shift_start_at,expected_assigned_at",
    [(0, 2, 2), (0, 0, 0)],
)
def test_assignement_within_shift(creation_at, shift_start_at, expected_assigned_at):

    rider = [
        Rider(
            id=1, shift_start_at=shift_start_at, shift_end_at=4, starting_point=(1, 1)
        )
    ]
    order = [
        Order(
            id=1,
            creation_at=creation_at,
            restaurant_address=(2, 2),
            customer_address=(3, 3),
        )
    ]
    dispatcher = Dispatcher(
        bag_limit=1,
        max_t=5,
        dim=5,
        orders=order,
        riders=rider,
    )
    for _ in range(expected_assigned_at + 1):
        dispatcher.step()
    assert dispatcher.orders[0].assigned_at == expected_assigned_at


@pytest.mark.parametrize(
    "creation_at,preparation_time,distance_to_vendor,expected_pick_up_at",
    [
        (0, 0, 0, 0),
        (0, 0, 2, 2),
        (0, 1, 0, 1),  # the rider does not have to travel
        (0, 1, 1, 1),  # the preparation = the rider distance time
        (0, 2, 1, 2),  # the preparation >= rider distance time
    ],
)
def test_pickup_after_prep_time_passed(
    creation_at, preparation_time, distance_to_vendor, expected_pick_up_at
):
    sp = (1, 1)
    rider = [Rider(id=1, shift_start_at=0, shift_end_at=4, starting_point=sp)]
    order = [
        Order(
            id=1,
            creation_at=creation_at,
            restaurant_address=(sp[0], sp[1] + distance_to_vendor),
            customer_address=(3, 3),
            preparation_time=preparation_time,
        )
    ]
    dispatcher = Dispatcher(
        bag_limit=1,
        max_t=5,
        dim=5,
        orders=order,
        riders=rider,
    )
    for _ in range(expected_pick_up_at + 1):
        dispatcher.step()
    assert dispatcher.orders[0].pick_up_at == expected_pick_up_at


@pytest.mark.parametrize(
    "creation_at,preparation_time,distance_to_vendor,expected_pick_up_at",
    [
        (0, 1, 0, 1),  # the rider does not have to travel
        (0, 1, 1, 1),  # the preparation = the rider distance time
        (0, 2, 1, 2),  # the preparation >= rider distance time
    ],
)
def test_pickup_after_prep_time_passed_2orders(
    creation_at, preparation_time, distance_to_vendor, expected_pick_up_at
):
    sp = (1, 1)
    rider = [Rider(id=1, shift_start_at=0, shift_end_at=4, starting_point=sp)]
    order = [
        Order(
            id=0,
            creation_at=creation_at,
            restaurant_address=(sp[0], sp[1] + distance_to_vendor),
            customer_address=(3, 3),
            preparation_time=0,
        ),
        Order(
            id=1,
            creation_at=creation_at,
            restaurant_address=(sp[0], sp[1] + distance_to_vendor),
            customer_address=(3, 3),
            preparation_time=preparation_time,
        ),
    ]
    dispatcher = Dispatcher(
        bag_limit=2,
        max_t=5,
        dim=5,
        orders=order,
        riders=rider,
    )
    for _ in range(expected_pick_up_at + 1):
        dispatcher.step()
    assert dispatcher.orders[0].pick_up_at == distance_to_vendor
    assert dispatcher.orders[1].pick_up_at == expected_pick_up_at
