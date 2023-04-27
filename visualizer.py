import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

class Visualizer:
    def __init__(self, num_iters: int, num_points: int, num_centers: int, grid_limit: int, px: List[int], py: List[int], cx: List[List[int]], cy: List[List[int]], pt_centers: List[List[int]]):
        self.num_iters = num_iters
        self.num_points = num_points
        self.num_centers = num_centers
        self.grid_limit = grid_limit

        self.px = px
        self.py = py
        self.cx = cx
        self.cy = cy
        self.pt_centers = pt_centers
    
    def get_points_by_center(self, iter_num: int) -> Tuple[Dict[int, List[int]], Dict[int, List[int]]]:
        points_x_by_center = {center_num: [] for center_num in range(self.num_centers)}
        points_y_by_center = {center_num: [] for center_num in range(self.num_centers)}
        for point_num in range(self.num_points):
            pt_center_num = self.pt_centers[iter_num][point_num]
            pt_center_num = int(pt_center_num.as_string())
            assert pt_center_num in points_x_by_center
            assert pt_center_num in points_y_by_center
            points_x_by_center[pt_center_num].append(int(self.px[point_num].as_string()))
            points_y_by_center[pt_center_num].append(int(self.py[point_num].as_string()))
        return points_x_by_center, points_y_by_center
    
    def visualize(self):
        # figure, axis = plt.subplots(self.num_iters, 1)
        for iter_num in range(self.num_iters):
            # set limits of coordinates of graph
            _, ax = plt.subplots()
            ax.set(xlim=(-self.grid_limit-1, self.grid_limit+1), ylim=(-self.grid_limit-1, self.grid_limit+1), aspect='equal')

            # get points for each center in this iteration
            points_x_by_center, points_y_by_center = self.get_points_by_center(iter_num)
            for center_num in range(self.num_centers):
                ax.scatter([int(self.cx[iter_num][center_num].as_string())], [int(self.cy[iter_num][center_num].as_string())], marker='o', c='#000')
                ax.annotate(f"c_{center_num}", (int(self.cx[iter_num][center_num].as_string()), int(self.cy[iter_num][center_num].as_string())))
                x = points_x_by_center[center_num]
                y = points_y_by_center[center_num]
                ax.scatter(x, y)
                for i in range(len(x)):
                    ax.annotate(center_num, (x[i], y[i]))
            plt.show()