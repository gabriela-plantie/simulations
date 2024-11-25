import random

from scripts.optim.utils import (
    Point,
    calculate_distances_dict,
    calculate_path_len,
    initialize_route_with_logic,
    two_swap,
)


class XOpts:
    def __init__(self, original_route: list[Point], current_position: Point):
        # TODO: implement precalculated distances when cases with a lot of elements

        self.original_route = original_route
        self.distances_dict = calculate_distances_dict(
            [current_position] + original_route
        )
        self.current_position = current_position

    def two_opt(self, route: list[Point]):
        """
        Has to have the current position, Restaurant as fixed.
        """
        distance = calculate_path_len([self.current_position] + route)
        for i in range(len(route) - 1):
            for j in range(i + 1, len(route)):
                # TODO optimize to avoid doing the swap, by calculating first
                # changes in distances
                # dist_if_maintain (between i and i+1 and j and j+1)
                # dist if change (btween i and j+1 and i+1 and j)

                possible_route = two_swap(route, i, j)
                possible_distance = calculate_path_len(
                    [self.current_position] + possible_route
                )

                # if the change is equally good -> swap
                if possible_distance < distance:
                    route = possible_route
                    distance = possible_distance
        return distance, route

    def local_search(self):
        route = self.original_route.copy()
        distance, route = initialize_route_with_logic(
            distance_dict=self.distances_dict, route=[self.current_position] + route
        )
        new_distance = distance - 1
        not_improving_iterations = 0
        while (new_distance < distance) or (not_improving_iterations < 5):
            random_route = self.original_route.copy()
            random.shuffle(random_route)
            new_distance, new_route = self.two_opt(
                initialize_route_with_logic(
                    distance_dict=self.distances_dict,
                    route=[self.current_position] + random_route,
                )[1]
            )
            if new_distance < distance:
                route = new_route
                distance = new_distance
            not_improving_iterations += 1
        return distance, route

    # TODO:
    # abstract class: initialize many rounds random (another level, superior to 2 opt)
    # Add simulated annealing
