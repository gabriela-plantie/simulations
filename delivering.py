from mesa import DataCollector, Model, space, time

from agents.riders import RiderStatus
from utils import RiderGenerator


class Dispatcher(Model):
    def __init__(self, dim, orders, num_riders, max_t, bag_limit):
        super().__init__()
        self.datacollector = DataCollector(
            # model_reporters={"mean_age": lambda m: m.agents.agg("age", np.mean)},
            agent_reporters={"State": "state"}
        )
        self.bag_limit = bag_limit
        self.max_t = max_t
        self.t: int = 0
        self.grid = space.MultiGrid(width=dim, height=dim, torus=True)
        self.schedule = time.RandomActivation(self)
        self.orders = orders
        self.riders = RiderGenerator(model=self, num_riders=num_riders).create_riders()
        self.orders_to_assign = []

    def step(self):
        self.get_orders_to_assign()
        self.assign_orders()

        self.agents.do("step")
        self.datacollector.collect(self)
        self.schedule.step()

        self.t += 1
        if self.t > self.max_t:  # FIXME: t should
            print("Max simulation steps reached!")
            return

    def get_orders_to_assign(self):
        # filter orders in state assigned from orders to assign
        for o in self.get_orders_assigned():  # move to rider.add_order_to_queue
            if o in self.orders_to_assign:
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
                    (a.state == RiderStatus.RIDER_FREE)
                    or (
                        (a.state == RiderStatus.RIDER_GOING_TO_VENDOR)
                        and (len(a.queue) + len(a.bag) < self.bag_limit)
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
            for rider in available_riders:
                if (
                    (rider.state == RiderStatus.RIDER_GOING_TO_VENDOR)
                    and (len(rider.queue) + len(rider.bag) < self.bag_limit)
                    and (rider.goal_position == order.restaurant_address)
                ):
                    rider.add_order_to_queue(order=order, t=self.t)
                    self.orders_to_assign.remove(order)

                    if (
                        len(rider.queue) + len(rider.bag) == self.bag_limit
                    ):  # CHECK tiene sentido?
                        available_riders.remove(rider)
                    break

            # if it cannot not then it adds it to the free riders
            if order in self.orders_to_assign[:]:
                for rider in list(
                    self.agents.select(lambda a: a.state == RiderStatus.RIDER_FREE)
                ):
                    rider.add_order_to_queue(order, self.t)
                    self.orders_to_assign.remove(order)
                    print(f"remueve {order}")
                    break
