import numpy as np
from mesa import Model, space, time

from agents.orders import Order
from agents.riders import Rider, RiderStatus


class OrderGenerator:
    def __init__(self, num_orders):
        self.num_orders = num_orders

    def __create_orders(self, times: int):
        return [self.num_orders] * times

    def __create_address(self, zone: int, dims: int = 10):
        x_max, y_max = (dims, dims)
        x, y = (
            np.random.normal(x_max // 2, x_max // 4),
            np.random.normal(y_max // 2, y_max // 4),
        )
        x = min(max(0, x), x_max) // 1
        y = min(max(0, y), y_max) // 1
        return x, y

    def create_orders(self, times):
        num_orders_per_timebucket = self.__create_orders(times)
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
        return orders


class Dispatcher(Model):
    def __init__(self, dim, num_orders, times, num_riders):
        super().__init__()
        self.t: int = 0
        self.grid = space.MultiGrid(width=dim, height=dim, torus=True)
        self.schedule = time.RandomActivation(self)
        self.orders = OrderGenerator(num_orders).create_orders(times)
        self.riders = [
            Rider(
                model=self,
                unique_id=r,
                shift_end_at=10,
                shift_start_at=0,
                state=RiderStatus.RIDER_FREE,
            )
            for r in range(num_riders)
        ]

        for rider in self.riders:
            self.grid.place_agent(rider, (2, 2))

    def step(self):
        # filter orders by creation time
        orders_at_t = self.orders[self.t]

        # assign order to rider (TODO filter by distance)
        free_riders = self.agents.select(lambda a: a.state == RiderStatus.RIDER_FREE)
        # free_riders = [r for r in self.riders if r.state
        # == RiderStatus.RIDER_FREE]

        # assign orders to rider
        num_orders_to_assing = min(len(free_riders), len(orders_at_t))
        for i in range(num_orders_to_assing):
            free_riders[i].add_order_to_queue(orders_at_t[i])

        self.agents.do("step")
        # self.datacollector.collect(self)
        self.schedule.step()

        self.t += 1
