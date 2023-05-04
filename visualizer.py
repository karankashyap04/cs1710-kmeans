import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

class Visualizer:
    def __init__(self, num_iters: int, num_points: int, num_centers: int, grid_limit: int, px: List[int], py: List[int], cx: List[List[int]], cy: List[List[int]], pt_centers: List[List[int]]):
        """
        __init__ function (constructor) for the Visualizer class.
        params:
            num_iters:   the total number of iterations for which the model produced an instance
            num_points:  the total number of datapoints in the instance produced by the model
            num_centers: the total number of centers (total number of clusters) in the instance
                         produced by the model
            grid_limit:  how far from the origin, in each of the cardinal directions, the
                         coordinate space was defined in the instance produced by the model
            px:          x coordinates of all the datapoints produced by the model (coordinate
                         for the i-th point is present at index i)
            py:          y coordinates of all the datapoints produced by the model (coordinate
                         for the i-th point is present at index i)
            cx:          x coordinates of all the centers across different iterations
                         (coordinate for j-th center during the i-th iteration is present at
                         row i and column j i.e. at cx[i][j])
            cy:          y coordinates of all the centers across different iterations
                         (coordinate for j-th center during the i-th iteration is present at
                         row i and column j i.e. at cy[i][j])
            pt_centers:  which center each point was assigned to across iterations (center
                         number of j-th point during the i-th iteration is present at row i
                         and column j i.e. at pt_centers[i][j])
        """
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
        """
        Identifies the points that are assigned to each center in the specified iteration.
        params:
            iter_num: which iteration to consider
        """
        points_x_by_center = {center_num: [] for center_num in range(self.num_centers)}
        points_y_by_center = {center_num: [] for center_num in range(self.num_centers)}
        for point_num in range(self.num_points):
            pt_center_num = self.pt_centers[iter_num][point_num]
            # pt_center_num = int(pt_center_num.as_string())
            assert pt_center_num in points_x_by_center
            assert pt_center_num in points_y_by_center
            points_x_by_center[pt_center_num].append(self.px[point_num])
            points_y_by_center[pt_center_num].append(self.py[point_num])
        return points_x_by_center, points_y_by_center
    
    def visualize(self):
        """
        Primary visualization code: defines matplotlib subplots, creates color-coded plots and
        displays them (creates and displays the visualization).
        """
        for iter_num in range(self.num_iters):
            # set limits of coordinates of graph
            _, ax = plt.subplots()
            ax.set(xlim=(-self.grid_limit-1, self.grid_limit+1), ylim=(-self.grid_limit-1, self.grid_limit+1), aspect='equal')

            # draw grid lines
            ax.grid(which='both', color='grey', linewidth=1, linestyle='-', alpha=0.2)

            # get points for each center in this iteration
            points_x_by_center, points_y_by_center = self.get_points_by_center(iter_num)
            for center_num in range(self.num_centers):
                x = points_x_by_center[center_num]
                y = points_y_by_center[center_num]
                ax.scatter(x, y)
                for i in range(len(x)):
                    ax.annotate(center_num, (x[i], y[i]))
                ax.scatter([int(self.cx[iter_num][center_num].as_string())], [int(self.cy[iter_num][center_num].as_string())], marker='o', c='#000', alpha=0.2)
                ax.annotate(f"c_{center_num}", (int(self.cx[iter_num][center_num].as_string()), int(self.cy[iter_num][center_num].as_string())))
            plt.show()
