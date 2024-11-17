from mesa import DataCollector, Model, space, time

from agents.riders import RiderStatus
from utils import OrderGenerator, RiderGenerator


class Dispatcher(Model):
    def __init__(self, dim, num_orders, times, num_riders):
        super().__init__()
        self.datacollector = DataCollector(
            # model_reporters={"mean_age": lambda m: m.agents.agg("age", np.mean)},
            agent_reporters={"State": "state"}
        )
        self.t: int = 0
        self.grid = space.MultiGrid(width=dim, height=dim, torus=True)
        self.schedule = time.RandomActivation(self)
        self.orders = OrderGenerator(num_orders).create_orders(times)
        self.riders = RiderGenerator(model=self, num_riders=num_riders).create_riders()
        self.orders_to_assign = []

    def step(self):
        self.get_orders_to_assign()
        self.assign_orders()

        self.agents.do("step")
        self.datacollector.collect(self)
        self.schedule.step()

        self.t += 1
        if self.t > len(self.orders):
            return

    def get_orders_to_assign(self):
        # filter orders in state assigned from orders to assign
        for o in self.get_orders_assigned():  # move to rider.add_order_to_queue
            if o in self.orders_to_assign:
                self.orders_to_assign.remove(o)

        # add new list of orders to "orders to assign" only if self.t <
        if self.t < len(self.orders):
            self.orders_to_assign.extend(self.get_new_orders_at_t())

    def get_orders_assigned(self):
        return [o for o in self.orders if o.assigned_at is not None]

    def get_new_orders_at_t(self):
        return [o for o in self.orders if o.creation_at == self.t]

    def assign_orders(self):
        # TODO filter by distance
        free_riders = list(
            self.agents.select(lambda a: a.state == RiderStatus.RIDER_FREE)
        )
        # free_riders = [r for r in self.riders if r.state
        # == RiderStatus.RIDER_FREE]

        # assign orders to rider
        # TODO add the case that I have orders from previous TB
        num_orders_to_assing = min(len(free_riders), len(self.orders_to_assign))
        for i in range(num_orders_to_assing):
            free_riders[i].add_order_to_queue(self.orders_to_assign[i], self.t)
