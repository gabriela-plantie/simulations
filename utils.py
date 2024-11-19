import numpy as np

from agents.orders import Order
from agents.riders import Rider


class RiderGenerator:
    def __init__(self, model, num_riders, starting_point):
        self.model = model
        self.num_riders = num_riders
        self.starting_point = starting_point

    def create_riders(self):
        riders = [
            Rider(
                model=self.model,
                unique_id=r,
                shift_end_at=10,
                shift_start_at=0,
            )
            for r in range(self.num_riders)
        ]

        for rider in riders:
            self.model.grid.place_agent(rider, self.starting_point)

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
