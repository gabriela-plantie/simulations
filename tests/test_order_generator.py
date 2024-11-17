import numpy as np

from agents.riders import RiderStatus
from delivering import Dispatcher, OrderGenerator


def test_create_orders():
    times = 100
    orders_per_tb = 10
    order_generator = OrderGenerator(orders_per_tb)
    orders = order_generator.create_orders(times)
    assert len(orders) == times
    assert [len(os) for os in orders] == [orders_per_tb] * times
    assert [o.id for os in orders for o in os] == list(
        range(times * orders_per_tb)
    ), "ids incorrectly created"


def test_dispatcher():
    num_riders = 20
    num_orders = 5
    times = 5
    dispatcher = Dispatcher(
        dim=5,
        num_orders=num_orders,
        times=times,
        num_riders=num_riders,
    )
    assert len(dispatcher.riders) == num_riders
    dispatcher.step()
    assert set([r.state for r in dispatcher.riders][:num_orders]) == set(
        [RiderStatus.RIDER_GOING_TO_VENDOR]
    )
    assert set([r.state for r in dispatcher.riders][num_orders:]) == set(
        [RiderStatus.RIDER_FREE]
    )
    dispatcher.step()
    assert set([r.state for r in dispatcher.riders][num_orders:]).issuperset(
        set([RiderStatus.RIDER_FREE, RiderStatus.RIDER_GOING_TO_VENDOR])
    )


def test_states():
    np.random.seed(19)
    num_riders = 2
    num_orders = 2
    times = 10
    dispatcher = Dispatcher(
        dim=5,
        num_orders=num_orders,
        times=times,
        num_riders=num_riders,
    )
    assert dispatcher.riders[0].queue == []
    dispatcher.step()
    assert len(dispatcher.riders[0].queue) == 1
    # assert rider state is rider going to vendor
    assert dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR

    # check status change from going to vendor to going to customer
    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_VENDOR:
        dispatcher.step()
    assert len(dispatcher.riders[0].queue) == 0  # TODO change when stacking is allowed
    assert len(dispatcher.riders[0].bag) >= 1  # TODO change when stacking is allowed

    while dispatcher.riders[0].state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
        dispatcher.step()
    assert len(dispatcher.riders[0].bag) == 0
