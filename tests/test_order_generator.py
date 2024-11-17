import numpy as np

from agents.riders import RiderStatus
from delivering import Dispatcher
from utils import OrderGenerator


def test_create_orders():
    times = 100
    orders_per_tb = 10
    orders = OrderGenerator(orders_per_tb).create_orders(times)
    assert max([o.creation_at for o in orders]) == times - 1
    assert len(orders) == orders_per_tb * times
    assert [o.id for o in orders] == list(
        range(times * orders_per_tb)
    ), "ids incorrectly created"


def test_dispatcher():
    num_riders = 20
    orders_per_tb = 5
    times = 5
    orders = OrderGenerator(orders_per_tb).create_orders(times)
    dispatcher = Dispatcher(
        dim=5,
        orders=orders,
        num_riders=num_riders,
    )
    assert len(dispatcher.riders) == num_riders
    dispatcher.step()
    assert set([r.state for r in dispatcher.riders][:orders_per_tb]) == set(
        [RiderStatus.RIDER_GOING_TO_VENDOR]
    )
    assert set([r.state for r in dispatcher.riders][orders_per_tb:]) == set(
        [RiderStatus.RIDER_FREE]
    )
    dispatcher.step()
    assert set([r.state for r in dispatcher.riders][orders_per_tb:]).issuperset(
        set([RiderStatus.RIDER_FREE, RiderStatus.RIDER_GOING_TO_VENDOR])
    )


def test_states():
    np.random.seed(19)
    num_riders = 2
    num_orders = 2
    times = 10
    orders = OrderGenerator(num_orders).create_orders(times)
    dispatcher = Dispatcher(
        dim=5,
        orders=orders,
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


def test_orders_times_steps():
    np.random.seed(19)
    num_riders = 1
    num_orders = 1
    times = 10

    orders = OrderGenerator(num_orders).create_orders(times)
    dispatcher = Dispatcher(
        dim=5,
        orders=orders,
        num_riders=num_riders,
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
