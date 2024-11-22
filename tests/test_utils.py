from scripts.optim.utils import Point, calculate_distances_dict, calculate_path_len
from scripts.utils import OrderGenerator


def test_create_orders():
    times = 100
    orders_per_tb = 10
    orders = OrderGenerator(orders_per_tb).create_orders(times)
    assert max([o.creation_at for o in orders]) == times - 1
    assert len(orders) == orders_per_tb * times
    assert [o.id for o in orders] == list(
        range(times * orders_per_tb)
    ), "ids incorrectly created"


def test_calculate_path_len():
    """
    ooooo
    o1ooo
    oo2oo
    o0ooo

    """

    sorted_orders = [
        Point(id=0, x=1, y=0),
        Point(id=2, x=2, y=1),
        Point(id=1, x=1, y=2),
    ]

    assert calculate_path_len(sorted_orders) == 4


def tests_calculate_distances_dict():
    points = [Point(id=0, x=1, y=0), Point(id=1, x=1, y=2), Point(id=2, x=2, y=1)]

    assert calculate_distances_dict(points) == {
        0: {1: 2, 2: 2},
        1: {0: 2, 2: 2},
        2: {0: 2, 1: 2},
    }
