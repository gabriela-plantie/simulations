class Order:
    def __init__(
        self,
        id: int,
        creation_at: int,
        preparation_time: int,
        restaurant_address: int,
        customer_address: int,
    ):
        self.id = id
        self.creation_at = creation_at
        self.preparation_time = preparation_time
        self.restaurant_address = restaurant_address
        self.customer_address = customer_address
        self.assigned_at = None
        self.pick_up_at = None
        self.drop_off_at = None

    def rider_assign(self, assigned_at):
        self.assigned_at = assigned_at

    def rider_pick_up(self, pick_up_at):
        if self.assigned_at is None:
            raise TypeError("Assignement time missing for order to pick up.")
        self.pick_up_at = pick_up_at

    def rider_drop_off(self, drop_off_at):
        if self.assigned_at is None or self.pick_up_at is None:
            raise TypeError("Previous time steps missing for order to drop off.")
        self.drop_off_at = drop_off_at
