from ortools.linear_solver import pywraplp

from scripts.optim.utils import Point, length

solver_status = {
    pywraplp.Solver.__dict__[status]: status
    for status in [
        "OPTIMAL",
        "FEASIBLE",
        "INFEASIBLE",
        "ABNORMAL",
        "UNBOUNDED",
        "MODEL_INVALID",
        "NOT_SOLVED",
    ]
}


class MipRiderVendor:
    def __init__(self):
        pass

    def optimize_rider_to_vendor(
        self,
        idle_riders,
        orders_to_assign,
    ):

        restaurants = self.get_restaurants(orders_to_assign)
        orders_by_restaurant = self.get_orders_by_restaurant(
            orders_to_assign, restaurants
        )

        # TODO create a class for restaurant
        # add id of restaurant to order

        solver = pywraplp.Solver(
            "CBC_MIXED_INTEGER_PROGRAMMING",
            pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING,
        )

        # define variables
        rider_vendor = {}
        for rider in idle_riders:
            rider_vendor[rider.id] = {}
            for restaurant_id in restaurants.keys():
                var = f"rider{rider.id}-vendor{restaurant_id}"
                rider_vendor[rider.id][restaurant_id] = solver.IntVar(0, 1, name=var)

        rider_num_vendors = {}
        for rider in idle_riders:
            rider_num_vendors[rider.id] = sum(
                [
                    rider_vendor[rider.id][restaurant_id]
                    for restaurant_id in restaurants.keys()
                ]
            )

        vendor_num_riders = {}
        for vendor_id in restaurants.keys():
            vendor_num_riders[vendor_id] = sum(
                [rider_vendor[rider.id][vendor_id] for rider in idle_riders]
            )

        # NO PUEDE PASAR Q HAYA RIDERS LIBRES Y RESTAURANTS SIN RIDERS
        # vendor_num_riders[vendor_id] == 0 ->
        # rider_num_vendors[rider] > 0 para todo rider
        # V R          V  R
        # 0 0 -> F   # 0  0
        # 0 1 -> T   # 0  2
        # 1 0 -> T   # 2  0
        # 1 1 -> T   # 2  2

        for rider in idle_riders:
            solver.Add(
                constraint=(rider_num_vendors[rider.id] <= 1),
                name=f"rider {rider.id} must have max bag size vendors assigned",
            )

        for vendor_id in restaurants.keys():
            solver.Add(
                constraint=(vendor_num_riders[vendor_id] <= 1),
                name=f"vendor {vendor_id} must have max 1 rider assigned",
            )

        for vendor_id in restaurants.keys():
            for rider in idle_riders:
                solver.Add(
                    constraint=(
                        vendor_num_riders[vendor_id] + rider_num_vendors[rider.id] >= 1
                    ),
                    name=(
                        f"if rider {rider.id} free -> "
                        f"vendor {vendor_id} should have at least one rider"
                    ),
                )

        dist = {
            (r.id, rest_id): length(
                Point(rest_id, *restaurant_address), Point(r.id, *r.pos)
            )
            for rest_id, restaurant_address in restaurants.items()
            for r in idle_riders
        }

        # objective
        objective = 0
        for rider in idle_riders:
            for restaurant_id in restaurants.keys():
                objective += (
                    rider_vendor[rider.id][restaurant_id]
                    * dist[rider.id, restaurant_id]
                )

        solver.Minimize(objective)
        # get solution: rider and vendor

        # map assigned orders to vendor

        # TODO si un vendor tiene 10 ordenes, y otro 1
        # y solo tenemos 2 riders, y la bag capacity es de 5
        # deberia asignar ese mismo vendor a los dos riders
        # tambien se puede "partir" al vendor en differentes "subvendors"
        # si tiene mas de bag capacity orders

        status = solver.Solve()
        print(solver_status[status])

        rider_orders = {}
        for rider in idle_riders:
            rider_orders[rider.id] = []
            for restaurant_id in restaurants.keys():
                if rider_vendor[rider.id][restaurant_id].solution_value() == 1:
                    rider_orders[rider.id].extend(orders_by_restaurant[restaurant_id])

        return rider_orders

    def get_restaurants(self, orders_to_assign):
        restaurant_addresses = set(o.restaurant_address for o in orders_to_assign)
        restaurants = {i: pos for i, pos in enumerate(restaurant_addresses)}
        return restaurants

    def get_orders_by_restaurant(self, orders_to_assign, restaurants):
        orders_by_restaurant = {}
        for vendor_id, vendor_address in restaurants.items():
            orders_by_restaurant[vendor_id] = []
            for order in orders_to_assign:
                if order.restaurant_address == vendor_address:
                    orders_by_restaurant[vendor_id].append(order)

        return orders_by_restaurant
