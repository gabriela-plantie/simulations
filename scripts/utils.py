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
