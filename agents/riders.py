from enum import Enum

from mesa import Agent


class RiderStatus(str, Enum):
    RIDER_FREE = "rider is free"
    RIDER_GOING_TO_VENDOR = "rider is going to vendor"
    RIDER_GOING_TO_CUSTOMER = "rider is going to customer with the order"


class Rider(Agent):
    def __init__(self, unique_id, model, shift_start_at, shift_end_at, state):
        super().__init__(model=model)
        self.shift_start_at = shift_start_at
        self.shift_end_at = shift_end_at
        self.state = state
        self.queue = []
        self.bag = []
        self.goal_position = None

    def add_order_to_queue(self, order, t):
        self.queue.append(order)
        self.state = RiderStatus.RIDER_GOING_TO_VENDOR
        self.goal_position = order.restaurant_address
        order.rider_assign(t)

    def remove_order_from_queue(self, order):
        self.queue.remove(order)
        # if len(self.queue) == 0:
        #     self.state = RiderStatus.RIDER_GOING_TO_CUSTOMER

    def add_order_to_bag(self, order, t):
        self.bag.append(order)
        self.state = RiderStatus.RIDER_GOING_TO_CUSTOMER
        self.goal_position = order.customer_address
        order.rider_pick_up(t)

    def remove_order_from_bag(self, order, t):
        self.bag.remove(order)
        if len(self.bag) == 0:
            self.state = RiderStatus.RIDER_FREE
            # FOR NOW I assume they stay at the customer place
            # until new order is assigned
        order.rider_drop_off(t)

    def move(self):
        x, y = self.pos
        x_goal, y_goal = self.goal_position

        if x < x_goal:
            actual_position = (x + 1, y)
        elif x > x_goal:
            actual_position = (x - 1, y)
        elif y < y_goal:
            actual_position = (x, y + 1)
        elif y > y_goal:
            actual_position = (x, y - 1)

        self.model.grid.move_agent(agent=self, pos=actual_position)
        print("x")

    def step(self):
        if self.goal_position is None:
            return

        if self.pos == self.goal_position:
            if self.state == RiderStatus.RIDER_GOING_TO_VENDOR:
                order = self.queue[0]  # TODO attention when stacking
                self.add_order_to_bag(order, self.model.t)
                self.remove_order_from_queue(order)

            elif self.state == RiderStatus.RIDER_GOING_TO_CUSTOMER:
                order = self.bag[0]  # TODO attention when stacking
                self.remove_order_from_bag(order, self.model.t)

        elif self.pos != self.goal_position:
            self.move()
