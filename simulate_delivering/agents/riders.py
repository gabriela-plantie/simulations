from mesa import Agent


class Rider:
    def __init__(self, id, shift_start_at, shift_end_at, starting_point):
        self.id = id
        self.shift_start_at = shift_start_at
        self.shift_end_at = shift_end_at
        self.starting_point = starting_point


class RiderAgent(Agent):
    def __init__(self, id, model, shift_start_at, shift_end_at, starting_point):
        super().__init__(model=model)
        self.id = id
        self.shift_start_at = shift_start_at
        self.shift_end_at = shift_end_at
        self.starting_point = starting_point
        self._queue = []
        self._bag = []
        self._goal_position = None

    def _add_order_to_queue(self, order, t):
        self._queue.append(order)
        self._goal_position = order.restaurant_address
        order._rider_assign(assigned_at=t)

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
        if self.rider_has_bag():
            self._goal_position = self._bag[0].customer_address

        order._rider_drop_off(t=t, rider_id=self.id)

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
        if self.rider_reached_goal_position():
            self._handle_reached_goal()
        else:
            self.move()

    def count_items_in_queue(self):
        return len(self._queue)

    def count_items_in_bag(self):
        return len(self._bag)

    def rider_has_bag(self):
        return self.count_items_in_bag() > 0

    def rider_has_queue(self):
        return self.count_items_in_queue() > 0

    def rider_shift_started(self, t):
        return self.shift_start_at <= t

    def rider_shift_ended(self, t):
        return self.shift_end_at <= t

    def rider_shift_within_time_limits(self, t):
        return self.rider_shift_started(t) and not self.rider_shift_ended(t)

    def rider_is_going_to_vendor(self):
        return self.rider_has_queue() and not self.rider_has_bag()

    def rider_is_waiting_at_vendor_for_pickups(self):
        return (
            self.rider_has_queue() and self.rider_has_bag()
        )  # TODO ADD that is the same address

    def rider_is_going_to_this_vendor(self, order):
        return self._goal_position == order.restaurant_address

    def rider_is_going_to_customer(self):
        return self.rider_has_bag() and not self.rider_has_queue()

    def rider_going_to_customer_overtime(self, t):
        return self.rider_is_going_to_customer() and self.rider_shift_ended(t)

    def rider_is_idle(self, t):
        return (
            self.rider_shift_within_time_limits(t)
            and not self.rider_has_queue()
            and not self.rider_has_bag()
            # en data collector que corre despues de rider step,
            # tira q un rider esta idle pero ya entrego su orden!!!
            and not self.rider_delivered_at_this_time(t)
        )

    def rider_delivered_at_this_time(self, t):
        return self.id in [
            o.delivered_by for o in self.model.orders if o.drop_off_at == t
        ]

    def rider_can_accept_orders(self, bag_limit, t):
        return (
            self.rider_shift_within_time_limits(t)
            and self.rider_has_capacity_in_bag(bag_limit)
            and not self.rider_is_going_to_customer()
            # because for now stacking is allowed only at same vendor
        )

    def rider_finished_pickup(self):
        return self.rider_has_bag() and not self.rider_has_queue()

    def rider_has_capacity_in_bag(self, bag_limit):
        return self.count_items_in_queue() + self.count_items_in_bag() < bag_limit

    def rider_reached_goal_position(self):
        return self.pos == self._goal_position

    def _pickup_orders(self):
        for order in self._queue[:]:
            if order.order_is_ready(self.model.t):
                self._add_order_to_bag(order, self.model.t)
                self._remove_order_from_queue(order)

        if self.rider_finished_pickup():
            self.model.sort_orders_in_bag(self)  # Ordena los pedidos en la bolsa
            self._goal_position = self._bag[0].customer_address

    def _deliver_order(self):
        if self.rider_has_bag():
            self._remove_order_from_bag(self._bag[0], self.model.t)
        else:
            raise ValueError("Rider has no bag to deliver from")

    def _handle_reached_goal(self):
        if (
            self.rider_is_going_to_vendor()
            or self.rider_is_waiting_at_vendor_for_pickups()
        ):
            self._pickup_orders()
        elif self.rider_is_going_to_customer():
            self._deliver_order()
        # else:
        #     print(f"Rider {self.id} idle")

    def reorder_bag(self, ordered_bag):
        self._rider_bag = ordered_bag
        self.goal_position = self._bag[0].customer_address
