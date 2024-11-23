import numpy as np

from scripts.optim.utils import Point, calculate_distances_dict, calculate_path_len


class XOpts:
    def __init__(self, original_route):
        # TODO: implement precalculated distances when cases with a lot of elements
        self.distances_dict = calculate_distances_dict(original_route)
        self.original_route = original_route

    @staticmethod
    def _two_swap(route: list[Point], i: int, j: int):
        """
        - i and j are positions.
        - j > i
        - if it takes a route that crosses over itself -> untangles it
        """
        # assert i<j
        if j < (len(route) - 1):
            route = route[:i] + list(np.flipud(route[i : j + 1])) + route[j + 1 :]
        else:
            # if j == len(route)
            route = route[:i] + list(np.flipud(route[i:]))
        #  assert len(path) == len(set(path))
        #  assert set(route) == set(path)
        return route

    def two_opt(self, current_position):
        """
        Has to have the current position, Restaurant as fixed.
        """
        route = self.original_route.copy()
        distance = calculate_path_len([current_position] + route)
        for i in range(len(route) - 1):
            for j in range(i + 1, len(route)):
                # TODO optimize to avoid doing the swap, by calculating first
                # changes in distances
                # dist_if_maintain (between i and i+1 and j and j+1)
                # dist if change (btween i and j+1 and i+1 and j)

                possible_route = self._two_swap(route, i, j)
                possible_distance = calculate_path_len(
                    [current_position] + possible_route
                )

                # if the change is equally good -> swap
                if possible_distance < distance:
                    route = possible_route
                    distance = possible_distance
        return distance, route

    # TODO:
    # abstract class: initialize many rounds random (another level, superior to 2 opt)
    # Add simulated annealing
