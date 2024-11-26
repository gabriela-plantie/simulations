from enum import Enum

from mesa import Agent


class RiderStatus(str, Enum):
    RIDER_UNAVAILABLE = "rider is unavailable"
    RIDER_FREE = "rider is free"
    RIDER_GOING_TO_VENDOR = "rider is going to vendor"
    RIDER_GOING_TO_CUSTOMER = "rider is going to customer with the order"


class Rider:
    def __init__(self, id, shift_start_at, shift_end_at, starting_point):
        self.id = id
        self.shift_start_at = shift_start_at
        self.shift_end_at = shift_end_at
        self.starting_point = starting_point


class RiderAgent(Agent):
    def __init__(self, id, model, shift_start_at, shift_end_at, starting_point):
        super().__init__(model=model)
        self.shift_start_at = shift_start_at
        self.shift_end_at = shift_end_at
        self.starting_point = starting_point
        self.state = RiderStatus.RIDER_FREE
        self._queue = []
        self._bag = []
        self._goal_position = None

    def _add_order_to_queue(self, order, t):
        self._queue.append(order)
        self._goal_position = order.restaurant_address
        order._rider_assign(assigned_at=t)
        self.state = RiderStatus.RIDER_GOING_TO_VENDOR

    def _remove_order_from_queue(self, order):
        self._queue.remove(order)

    def _add_order_to_bag(self, order, t):
        self._bag.append(order)
        order._rider_pick_up(t)

    def _remove_order_from_bag(self, order, t):
        """
        Remove order from bag when delivered.
        Update goal position for rider:
            - if bag still has orders -> customer address
            - if bag empty -> remains
        """
        self._bag.remove(order)
        if len(self._bag) > 0:
            self._goal_position = self._bag[0].customer_address
        order._rider_drop_off(t)
        if len(self._bag) == 0:
            self.state = RiderStatus.RIDER_FREE

    def move(self):
        x, y = self.pos
        x_goal, y_goal = self._goal_position

        if x < x_goal:
            actual_position = (x + 1, y)
        elif x > x_goal:
            actual_position = (x - 1, y)
        elif y < y_goal:
            actual_position = (x, y + 1)
        elif y > y_goal:
            actual_position = (x, y - 1)

        self.model.grid.move_agent(agent=self, pos=actual_position)

    def step(self):

        if (
            (self.shift_end_at <= self.model.t)
            and (self.count_items_in_bag() == 0)
            and (self.count_items_in_queue() == 0)
        ):
            self.state = RiderStatus.RIDER_UNAVAILABLE

        if self._goal_position is None:
            return
        if self.rider_reached_goal_position():
            self._handle_reached_goal()
        else:
            self.move()

    def rider_finished_pickup(self):
        return (len(self._queue) == 0) and (len(self._bag) > 0)

    def rider_has_capacity_in_bag(self, bag_limit):
        has_capacity = len(self._queue) + len(self._bag) < bag_limit
        return has_capacity and (self.state != RiderStatus.RIDER_UNAVAILABLE)

    def rider_is_going_to_this_vendor(self, order):
        return self._goal_position == order.restaurant_address

    def rider_is_free(self, t):
        return self.state == RiderStatus.RIDER_FREE and self.shift_start_at <= t

    def rider_reached_goal_position(self):
        return self.pos == self._goal_position

    def _pickup_orders(self):
        for order in self._queue[:]:
            if order.order_is_ready(self.model.t):
                self._add_order_to_bag(order, self.model.t)
                self._remove_order_from_queue(order)

        if self.rider_finished_pickup():
            self.model.sort_orders_in_bag(self)  # Ordena los pedidos en la bolsa
            self.state = RiderStatus.RIDER_GOING_TO_CUSTOMER

    def _deliver_order(self):
        if self._bag:
            order = self._bag[0]
            self._remove_order_from_bag(order, self.model.t)

    def _handle_reached_goal(self):
        if self.state == RiderStatus.RIDER_GOING_TO_VENDOR:
            self._pickup_orders()
        elif self.state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
            self._deliver_order()

    def reorder_bag(self, ordered_bag):
        self._rider_bag = ordered_bag
        self.goal_position = self._bag[0].customer_address

    def count_items_in_bag(self):
        return len(self._bag)

    def count_items_in_queue(self):
        return len(self._queue)
