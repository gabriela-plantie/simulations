import numpy as np
from mesa import DataCollector, Model, space, time

from agents.riders import RiderStatus
from utils import RiderGenerator


class Dispatcher(Model):
    def __init__(
        self,
        dim,
        orders,
        riders,
        max_t,
        bag_limit,
        slowness=1,
    ):
        super().__init__()
        self.datacollector = DataCollector(
            # model_reporters={"mean_age": lambda m: m.agents.agg("age", np.mean)},
            # agent_reporters={"State": "state"}
            {
                "riders_free": lambda m: sum(
                    [r.state == RiderStatus.RIDER_FREE for r in m.riders]
                ),
                "riders_going_to_vendor": lambda m: sum(
                    [r.state == RiderStatus.RIDER_GOING_TO_VENDOR for r in m.riders]
                ),
                "riders_going_to_customer": lambda m: sum(
                    [r.state == RiderStatus.RIDER_GOING_TO_CUSTOMER for r in m.riders]
                ),
                "orders_delivered": lambda m: sum(
                    [o.drop_off_at is not None for o in m.orders]
                ),
                "orders_waiting": lambda m: sum(
                    [(o.assigned_at is None) for o in m.orders]
                ),
                "delivery_time": lambda m: np.mean(
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
                "orders_assigned": lambda m: sum(
                    [o.assigned_at is not None for o in m.orders]
                ),
                "orders_picked_up": lambda m: sum(
                    [o.pick_up_at is not None for o in m.orders]
                ),
            }
        )
        self.bag_limit = bag_limit
        self.max_t = max_t
        self.t: int = 0
        self.grid = space.MultiGrid(width=dim, height=dim, torus=True)
        self.schedule = time.RandomActivation(self)
        self.orders = orders
        self.riders = RiderGenerator(model=self, riders=riders).create_agents()
        self.orders_to_assign = []
        self.slowness = slowness
        self.sub_t = 0

    def step(self):
        self.datacollector.collect(self)
        self.sub_t += 1
        if self.sub_t < self.slowness:
            return
        self.sub_t = self.sub_t % self.slowness

        self.get_orders_to_assign()
        self.assign_orders()

        self.agents.do("step")

        self.schedule.step()

        self.t += 1
        if self.t > self.max_t:  # FIXME: t should
            print("Max simulation steps reached!")
            return

    def get_orders_to_assign(self):
        orders_to_assign = self.get_orders_assigned()
        # filter orders in state assigned from orders to assign
        for o in orders_to_assign[:]:  # move to rider.add_order_to_queue
            # TODO add a test for the copy -> assign many orders while rider going.
            if o in self.orders_to_assign[:]:
                self.orders_to_assign.remove(o)

        # add new list of orders to "orders to assign" only if self.t <
        self.orders_to_assign.extend(self.get_new_orders_at_t())

    def get_orders_assigned(self):
        return [o for o in self.orders if o.assigned_at is not None]

    def get_new_orders_at_t(self):
        return [o for o in self.orders if o.creation_at == self.t]

    def get_available_riders(self):
        """
        Get available riders:
            - riders that are free or
            - riders that are going to the vendor and have space in the queue
        """
        return list(
            self.agents.select(
                lambda a: (
                    (a.shift_start_at <= self.t)
                    and (
                        (a.state == RiderStatus.RIDER_FREE)
                        or (
                            (a.state == RiderStatus.RIDER_GOING_TO_VENDOR)
                            and (len(a._queue) + len(a._bag) < self.bag_limit)
                        )
                    )
                )
            )
        )

    def assign_orders(self):
        available_riders = self.get_available_riders()
        # For now, we will allow stacking only at the vendor
        # assign orders to rider
        for order in self.orders_to_assign[:]:

            # first tries to add the order
            # to a rider that is already going to the vendor
            for rider in available_riders[:]:
                if (
                    (rider.state == RiderStatus.RIDER_GOING_TO_VENDOR)
                    and (len(rider._queue) + len(rider._bag) < self.bag_limit)
                    and (rider._goal_position == order.restaurant_address)
                ):
                    rider.add_order_to_queue(order=order, t=self.t)
                    self.orders_to_assign.remove(order)

                    if (
                        len(rider._queue) + len(rider._bag) == self.bag_limit
                    ):  # CHECK tiene sentido?
                        available_riders.remove(rider)
                    break

            # if it cannot not then it adds it to the free riders
            if order in self.orders_to_assign[:]:
                for rider in list(
                    self.agents.select(
                        lambda a: (
                            (a.shift_start_at <= self.t)
                            and (a.state == RiderStatus.RIDER_FREE)
                        )
                    )
                ):
                    rider.add_order_to_queue(order, self.t)
                    self.orders_to_assign.remove(order)
                    break
