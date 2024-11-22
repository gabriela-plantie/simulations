from enum import Enum

from mesa import Agent


class RiderStatus(str, Enum):
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

    def add_order_to_queue(self, order, t):
        self._queue.append(order)
        self._goal_position = order.restaurant_address
        order.rider_assign(assigned_at=t)
        self.state = RiderStatus.RIDER_GOING_TO_VENDOR

    def remove_order_from_queue(self, order):
        self._queue.remove(order)

    def add_order_to_bag(self, order, t):
        self._bag.append(order)
        order.rider_pick_up(t)

    def remove_order_from_bag(self, order, t):
        """
        Remove order from bag when delivered.
        Update goal position for rider:
            - if bag still has orders -> customer address
            - if bag empty -> remains
        """
        self._bag.remove(order)
        if len(self._bag) > 0:
            self._goal_position = self._bag[0].customer_address
        order.rider_drop_off(t)
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
        if self._goal_position is None:
            return

        if self.pos == self._goal_position:
            if self.state == RiderStatus.RIDER_GOING_TO_VENDOR:
                for order in self._queue[:]:
                    if order.creation_at + order.preparation_time <= self.model.t:
                        self.add_order_to_bag(order, self.model.t)
                        self.remove_order_from_queue(order)

                if (len(self._queue) == 0) and (len(self._bag) > 0):
                    self.model.sort_orders_in_bag(self)
                    self.state = RiderStatus.RIDER_GOING_TO_CUSTOMER

            elif self.state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
                order = self._bag[0]
                self.remove_order_from_bag(order, self.model.t)

        elif self.pos != self._goal_position:
            self.move()
