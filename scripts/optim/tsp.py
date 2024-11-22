import numpy as np

from scripts.optim.utils import Point, calculate_distances_dict


class XOpts:
    def __init__(self, original_route):
        # TODO: implement precalculated distances when cases with a lot of elements
        self.distances_dict = calculate_distances_dict(original_route)

    @staticmethod
    def _two_swap(route: list[Point], i: int, j: int):
        next_i = (i + 1) % len(route)
        next_j = (j + 1) % len(route)
        if next_j > j:
            route = (
                route[:next_i] + list(np.flipud(route[next_i:next_j])) + route[next_j:]
            )
        else:
            route = route[next_j:next_i] + list(np.flipud(route[next_i:]))
        #  assert len(path) == len(set(path))
        #   assert set(route) == set(path)
        return route

    def _two_opt(self, distance, route):
        for i in range(len(route) - 1):
            for j in range(i + 1, len(route)):

                dist_keep = (
                    self.distances_dict[route[i], route[(i + 1) % len(route)]]
                    + self.distances_dict[route[j], route[(j + 1) % len(route)]]
                )

                dist_change = (
                    self.distances_dict[route[i], route[j]]
                    + self.distances_dict[
                        route[(i + 1) % len(route)], route[(j + 1) % len(route)]
                    ]
                )

                # if the change is equally good -> swap
                if dist_change < dist_keep:
                    new_route = self._two_swap(route, i, j)
                    distance = distance - dist_keep + dist_change
                    # print(f"i {i} - j {j} - distance {distance}")
                    route = new_route
        return distance, route

    # simulated annealing
