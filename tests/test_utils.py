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
