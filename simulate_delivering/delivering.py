from mesa import DataCollector, Model, space, time

from simulate_delivering.optim_routes.mip_rider_to_vendor import MipRiderVendor
from simulate_delivering.optim_routes.tsp import LocalSearch
from simulate_delivering.optim_routes.utils import (
    Point,
    orders_to_points,
    points_to_orders,
)
from simulate_delivering.utils import RiderGenerator, data_collector


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
            data_collector()
        )
        self.bag_limit = bag_limit
        self.max_t = max_t
        self.t: int = -1
        self.grid = space.MultiGrid(width=dim, height=dim, torus=True)
        self.schedule = time.RandomActivation(self)
        self.orders = orders
        self.riders = RiderGenerator(model=self, riders=riders).create_agents()
        self.orders_to_assign = []
        self.slowness = slowness
        self.sub_t = 0

    def step(self):
        self.t += 1
        self.sub_t += 1
        if self.sub_t < self.slowness:
            return
        self.sub_t = self.sub_t % self.slowness

        self.get_orders_to_assign()
        # self.assign_orders()
        self.assign_orders_mip()
        self.agents.do("step")

        self.schedule.step()
        self.datacollector.collect(self)

        if self.t > self.max_t:  # FIXME: t should
            print("Max simulation steps reached!")
            return

    def get_orders_to_assign(self):
        orders_assigned = self.get_orders_assigned()
        # filter orders in state assigned from orders to assign
        for o in orders_assigned[:]:  # move to rider.add_order_to_queue
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
        return list(
            self.agents.select(
                lambda a: a.rider_is_idle(t=self.t)
                or a.rider_has_capacity_in_bag(bag_limit=self.bag_limit)
            )
        )

    def get_idle_riders(self):
        return list(self.agents.select(lambda a: a.rider_is_idle(t=self.t)))

    def assign_orders(self):
        available_riders = self.get_available_riders()
        # For now, we will allow stacking only at the vendor
        # assign orders to rider
        for order in self.orders_to_assign[:]:

            # first tries to add the order
            # to a rider that is already going to the vendor
            self.assing_order_to_rider_going_to_vendor(available_riders, order)

            # if it cannot not then it adds it to the free riders
            if order in self.orders_to_assign[:]:
                for rider in self.get_idle_riders():
                    rider._add_order_to_queue(order, self.t)
                    self.orders_to_assign.remove(order)
                    break

    def assing_order_to_rider_going_to_vendor(self, available_riders, order):
        for rider in available_riders[:]:
            if rider.rider_is_going_to_this_vendor(
                order
            ) and rider.rider_can_accept_orders(bag_limit=self.bag_limit, t=self.t):
                rider._add_order_to_queue(order=order, t=self.t)
                self.orders_to_assign.remove(order)

                if not rider.rider_has_capacity_in_bag(self.bag_limit):
                    # CHECK tiene sentido?
                    available_riders.remove(rider)
                break

    def assign_orders_mip(self):
        # For now, we will allow stacking only at the vendor
        # while (len(self.get_idle_riders()) > 0) and (len(self.orders_to_assign) > 0):
        # TODO:
        # o mientras haya orders para asignar
        # y haya riders ocupados pero q pueden aceptar
        # y haya riders yendo a esos vendors
        # (costoso de chequear - variable por vendor?)

        for _ in range(2):
            print(f"time {self.t}")
            available_riders = self.get_available_riders()
            for order in self.orders_to_assign[:]:
                self.assing_order_to_rider_going_to_vendor(available_riders, order)
            self.assign_riders_to_vendor_mip()
        return None

    def assign_riders_to_vendor_mip(self):
        idle_riders = self.get_idle_riders()
        rider_orders = MipRiderVendor().optimize_rider_to_vendor(
            idle_riders=idle_riders,
            orders_to_assign=self.orders_to_assign.copy(),
        )

        for rider_id, orders in rider_orders.items():
            for order in orders:
                rider = self.get_rider_from_id(idle_riders, rider_id)
                # assign order to rider
                # TODO check queue capacity before add order to queue
                # rider.rider_can_accept_orders(bag_limit, t)
                if rider.rider_can_accept_orders(self.bag_limit, self.t):
                    rider._add_order_to_queue(order=order, t=self.t)
                    self.orders_to_assign.remove(order)

    def get_rider_from_id(self, riders, rider_id):
        return [rider for rider in riders if rider.id == rider_id][0]

    def sort_orders_in_bag(self, rider):
        """
        Since for now this only sorts in Restaurant
        -> Current pos is a restaurant.
        -> Point(restaurant) -> id=9999
        """

        # TODO: let's say that rider time should never be above some time.
        # and also DT < max(max_allowed_DT, prep_time + min_possible_rider_time)
        # now in reality rider time is preety fair, the problem is prep time.

        # rider._bag = sorted(rider._bag, key=lambda o: o.creation_at)
        if rider.count_items_in_bag() > 1:
            _, sorted_points = LocalSearch(
                original_route=orders_to_points(orders=rider._bag),
                current_position=Point(9999, *rider.pos),  # must be a point
            ).search()

            rider.reorder_bag(
                ordered_bag=points_to_orders(
                    points=sorted_points[1:], orders=rider._bag
                )
            )

        # TODO, stack and sort as long as max RIDER TIME is below sth
        # and avg RIDER TIME is sth.
