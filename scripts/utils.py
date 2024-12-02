import numpy as np

from scripts.agents.orders import Order
from scripts.agents.riders import RiderAgent


class RiderGenerator:
    def __init__(self, model, riders):
        self.model = model
        self.riders = riders

    def create_agents(self):
        riders = [
            RiderAgent(
                model=self.model,
                id=r.id,
                shift_start_at=r.shift_start_at,
                shift_end_at=r.shift_end_at,
                starting_point=r.starting_point,
            )
            for r in self.riders
        ]

        for rider in riders:
            self.model.grid.place_agent(rider, rider.starting_point)

        return riders


class OrderGenerator:
    def __init__(self, num_orders):
        self.num_orders = num_orders

    def __create_orders_distribution(self, times: int):
        return [self.num_orders] * times

    def __create_address(self, dims: int = 10):
        x_max, y_max = (dims - 1, dims - 1)
        x, y = (
            np.random.normal(x_max // 2, x_max // 4),
            np.random.normal(y_max // 2, y_max // 4),
        )
        x = min(max(0, x), x_max) // 1
        y = min(max(0, y), y_max) // 1
        return x, y

    def create_orders(self, times):
        num_orders_per_timebucket = self.__create_orders_distribution(times)
        orders = []
        previous_tot = 0
        for t, orders_tb in enumerate(num_orders_per_timebucket):
            orders_in_t = [
                Order(
                    id=previous_tot + i,
                    creation_at=t,
                    preparation_time=1,
                    restaurant_address=self.__create_address(2),
                    customer_address=self.__create_address(8),
                )
                for i in range(orders_tb)
            ]
            orders.append(orders_in_t)
            previous_tot = previous_tot + len(orders_in_t)
        return [o for ord in orders for o in ord]


def data_collector():
    return {
        "riders_in_shift": lambda m: sum(
            [r.rider_shift_within_time_limits(m.t) for r in m.riders]
        ),
        "riders_idle": lambda m: sum([r.rider_is_idle(m.t) for r in m.riders]),
        "riders_going_to_vendor": lambda m: sum(
            [r.rider_is_going_to_vendor() for r in m.riders]
        ),
        "riders_going_to_customer": lambda m: sum(
            [r.rider_is_going_to_customer() for r in m.riders]
        ),
        "riders_doing_overtime": lambda m: sum(
            [
                (r.rider_is_going_to_customer() or r.rider_is_going_to_vendor())
                and not r.rider_shift_within_time_limits(m.t)
                for r in m.riders
            ]
        ),
        "orders_created": lambda m: sum([(o.creation_at == m.t) for o in m.orders]),
        "orders_assigned": lambda m: sum([(o.assigned_at == m.t) for o in m.orders]),
        "orders_delivered": lambda m: sum([o.drop_off_at == m.t for o in m.orders]),
        "orders_waiting": lambda m: sum(
            [(o.assigned_at is None and o.creation_at <= m.t) for o in m.orders]
        ),
        "delivery_time": lambda m: np.mean(
            [
                (o.drop_off_at - o.creation_at)
                for o in m.orders
                if (
                    (o.creation_at <= m.t)
                    and (o.drop_off_at is not None)
                    and (o.drop_off_at >= m.t)
                )
            ]
        ),
        "delivery_time_cum": lambda m: np.mean(
            [
                (o.drop_off_at - o.creation_at)
                for o in m.orders
                if o.drop_off_at is not None
            ]
        ),
        "queue_size": lambda m: np.mean(
            [len(r._queue) for r in m.riders if len(r._queue) > 0]
        ),
        # TODO FIX warning mean of empty
        "bag_size": lambda m: np.mean(
            [len(r._bag) for r in m.riders if len(r._bag) > 0]
        ),
        "orders_assigned_cum": lambda m: sum(
            [o.assigned_at is not None for o in m.orders]
        ),
        "orders_picked_up_cum": lambda m: sum(
            [o.pick_up_at is not None for o in m.orders]
        ),
        "orders_delivered_cum": lambda m: sum(
            [o.drop_off_at is not None for o in m.orders]
        ),
    }
