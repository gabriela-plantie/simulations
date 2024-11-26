import random

from scripts.optim.utils import (
    Point,
    calculate_distances_dict,
    calculate_path_len,
    initialize_route_with_logic_from_restaurant,
    length,
    two_swap,
)


class LocalSearch:
    def __init__(self, original_route: list[Point], current_position: Point):
        # TODO: implement precalculated distances when cases with a lot of elements

        self.original_route = original_route
        self.distances_dict = calculate_distances_dict(
            [current_position] + original_route
        )
        self.current_position = current_position

    def two_opt_optimized(self, route_with_restaurant: list[Point]):
        """
        Has to have the current position, "restaurant", fixed.
        The optimized version, does not perform the swap to measure the differences
        in distances. On the contrary, it measures first only how much the distances
        will change and then if the total distance would be less, then swaps the
        positions.
        """

        distance = calculate_path_len(route_with_restaurant)
        for i in range(1, len(route_with_restaurant) - 1):
            # exludes the original point from the swap
            for j in range(i + 1, len(route_with_restaurant)):

                # dist_if_maintain (between i and i+1 and j and j+1)
                dist_if_maintain = (
                    length(route_with_restaurant[i - 1], route_with_restaurant[i])
                    + length(route_with_restaurant[j], route_with_restaurant[j + 1])
                    if j + 1 < len(route_with_restaurant)
                    else 0
                )

                # dist if change (between i and j+1 and i+1 and j)
                dist_if_change = (
                    length(route_with_restaurant[i - 1], route_with_restaurant[j])
                    + length(route_with_restaurant[i], route_with_restaurant[j + 1])
                    if j + 1 < len(route_with_restaurant)
                    else 0
                )

                if dist_if_change < dist_if_maintain:
                    route_with_restaurant = two_swap(route_with_restaurant, i, j)
                    distance = distance + dist_if_change - dist_if_maintain
        return distance, route_with_restaurant

    def two_opt(self, route_with_restaurant: list[Point]):
        """
        Has to have the current position, restaurant as fixed. Replaced by
        two_opt_optimized
        """
        distance = calculate_path_len(route_with_restaurant)
        for i in range(1, len(route_with_restaurant) - 1):
            # excludes the first element
            for j in range(i + 1, len(route_with_restaurant)):
                # TODO optimize to avoid doing the swap, by calculating first
                # changes in distances
                # dist_if_maintain (between i and i+1 and j and j+1)
                # dist if change (btween i and j+1 and i+1 and j)

                possible_route = two_swap(route_with_restaurant, i, j)
                possible_distance = calculate_path_len(possible_route)

                # if the change is equally good -> swap
                if possible_distance < distance:
                    print(f"2swap {i}{j}")
                    route_with_restaurant = possible_route
                    distance = possible_distance
        return distance, route_with_restaurant

    def search(self):
        route = self.original_route.copy()
        distance, route = initialize_route_with_logic_from_restaurant(
            distance_dict=self.distances_dict,
            route_with_restaurant=[self.current_position] + route,
        )
        new_distance = distance - 1
        not_improving_iterations = 0
        while (new_distance < distance) or (not_improving_iterations < 5):
            random_route = self.original_route.copy()
            random.shuffle(random_route)
            new_distance, new_route = self.two_opt_optimized(
                route_with_restaurant=initialize_route_with_logic_from_restaurant(
                    distance_dict=self.distances_dict,
                    route_with_restaurant=[self.current_position] + random_route,
                )[1]
            )
            if new_distance < distance:
                route = new_route
                distance = new_distance
            not_improving_iterations += 1
        return distance, route

    # TODO:
    # Add simulated annealing
