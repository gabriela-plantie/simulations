from enum import Enum


class OrderStatus(str, Enum):
    ORDER_CREATED = "order has been created"
    ORDER_ASSIGNED = "order has been assigned"
    ORDER_IN_BAG = "order has been picked up"
    ORDER_COMPLETED = "order has been delivered"


class Order:
    def __init__(
        self,
        id: int,
        creation_at: int,
        preparation_time: int,
        restaurant_address: int,
        customer_address: int,
        # assigned_at:int=None,
        # pick_up_at:int=None,
        # dropp_off_at:int=None,
    ):
        self.id = id
        self.creation_at = creation_at
        self.preparation_time = preparation_time
        self.restaurant_address = restaurant_address
        self.customer_address = customer_address

    def rider_assign(self, assigned_at):
        self.assigned_at = assigned_at

    def rider_pick_up(self, pick_up_at):
        self.rider_pick_up = pick_up_at

    def rider_drop_off(self, drop_off_at):
        self.drop_off_at = drop_off_at
