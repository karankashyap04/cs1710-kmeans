from z3 import *
from visualizer import Visualizer

class KMeans(object):

    def __init__(self, num_iters: int, num_points: int, num_centers: int, grid_limit: int):
        """
        params:
            num_iters: number of iterations for which to run the algorithm
            num_points: number of datapoints
            num_centers: number of centers
            grid_limit: dimensions of the grid (ex: if grid_limit is 5, then the coordinates go from
                        -5.0 to 5.0 along both axes)
        """
        self.num_iters = num_iters
        self.num_points = num_points
        self.num_centers = num_centers
        self.grid_limit = grid_limit

        # Solver
        self.s = Solver()

        self.points_x = {i: Int(f"px_{i}") for i in range(self.num_points)}
        self.points_y = {i: Int(f"py_{i}") for i in range(self.num_points)}

        def create_x_centers(iter_num: int):
            # return {i: Int(f"cx_{i}_{iter_num}") for i in range(self.num_centers)}
            cx = Array(f"cx_{iter_num}", IntSort(), IntSort())
            for center_num in range(self.num_centers):
                cx = Store(cx, center_num, Int(f"cs_{center_num}_{iter_num}"))
            return cx
        def create_y_centers(iter_num: int):
            # return {i: Int(f"cy_{i}_{iter_num}") for i in range(self.num_centers)}
            cy = Array(f"cy_{iter_num}", IntSort(), IntSort())
            for center_num in range(self.num_centers):
                cy = Store(cy, center_num, Int(f"cy_{center_num}_{iter_num}"))
            return cy

        # self.centers_x = {i: Ints(f"cx_{i}") for i in range(self.num_centers)}
        # self.centers_y = {i: Ints(f"cy_{i}") for i in range(self.num_centers)}
        self.centers_x = {iter_num: create_x_centers(iter_num) for iter_num in range(self.num_iters)}
        self.centers_y = {iter_num: create_y_centers(iter_num) for iter_num in range(self.num_iters)}

        # center for some point
        def create_point_centers(iter_num: int):
            return {i: Int(f"center_{i}_{iter_num}") for i in range(num_points)}
        
        # self.point_centers = {i: Ints(f"center_{i}") for i in range(num_points)}
        self.point_centers = {iter_num: create_point_centers(iter_num) for iter_num in range(self.num_iters)}
        # Each point is mapped to an int which we will constrain such that it is equal to the key
        # corresponding to the center that is closest to the point

        # This dictionary will help us reverse index so we can go from the z3 variable to the int
        # which will allow us to key into the centers_x and centers_y hashmaps (or just provide
        # the center number for the distance function)
        # def create_center_var_to_center_nums(iter_num: int):
        #     return {self.point_centers[iter_num][i]: i for i in range(num_points)}
        # # self.center_var_to_center_num = {self.points_centers[i]: i for i in range(num_points)}
        # self.center_var_to_center_num = {iter_num: create_center_var_to_center_nums(iter_num) for iter_num in range(self.num_iters)}


        ## Enforcing constraints that should always be true:
        self.points_within_grid()
        self.no_duplicate_points()
        self.centers_within_grid()
        self.point_centers_are_valid_center_numbers()
        self.points_have_closest_center()
        self.centers_correctly_updated()


    ##### FUNCTIONS ENFORCING CONSTRAINTS ON SOLVER VARIABLES #####
    
    def points_within_grid(self): # Ensures that all points are within the defined grid
        print("points within grid")
        for i in range(self.num_points):
            self.s.add(And(self.points_x[i] >= -self.grid_limit, self.points_x[i] <= self.grid_limit))
            self.s.add(And(self.points_y[i] >= -self.grid_limit, self.points_y[i] <= self.grid_limit))
    
    def no_duplicate_points(self):
        print("no duplicate points")
        for i in range(self.num_points):
            for j in range(i+1, self.num_points, 1):
                px1, py1 = self.points_x[i], self.points_y[i]
                px2, py2 = self.points_x[j], self.points_y[j]
                self.s.add(Or(px1 != px2, py1 != py2))
    
    def centers_within_grid(self): # Ensures that all centers are within the defined grid
        print("centers within grid")
        for iter_num in range(self.num_iters):
            for i in range(self.num_centers):
                # self.s.add(And(self.centers_x[iter_num][i] >= -self.grid_limit, self.centers_x[iter_num][i] <= self.grid_limit))
                self.s.add(And(Select(self.centers_x[iter_num], i) >= -self.grid_limit, Select(self.centers_x[iter_num], i) <= self.grid_limit))
                # self.s.add(And(self.centers_y[iter_num][i] >= -self.grid_limit, self.centers_y[iter_num][i] <= self.grid_limit))
                self.s.add(And(Select(self.centers_y[iter_num], i) >= -self.grid_limit, Select(self.centers_y[iter_num], i) <= self.grid_limit))
    
    def point_centers_are_valid_center_numbers(self):
        print("point centers are valid center numbers")
        for iter_num in range(self.num_iters):
            for i in range(self.num_points):
                center_var = self.point_centers[iter_num][i]
                self.s.add(And(center_var >= 0, center_var < self.num_centers))
    
    # def points_have_closest_center(self):
    #     # self.s.push()
    #     for iter_num in range(self.num_iters):
    #         for point_num in range(self.num_points):
    #             # expected_center_num = self.get_min_dist_center(point_num, iter_num)
    #             # center_var = self.point_centers[iter_num][point_num]
    #             # self.s.add(self.center_var_to_center_num[iter_num][center_var] == expected_center_num)
    #             distances = []
    #             for center_num in range(self.num_centers):
    #                 distances.append(self.distance(point_num, center_num, iter_num))
    #             point_center_var = self.point_centers[iter_num][point_num] # z3 variable

    #     # self.s.pop()
    
    def points_have_closest_center(self):
        print("points have closest center")
        for iter_num in range(self.num_iters):
            for point_num in range(self.num_points):
                center_num_var = self.point_centers[iter_num][point_num]
                assigned_center_dist = self.distance(point_num, center_num_var, iter_num)
                for center_num in range(self.num_centers):
                    dist = self.distance(point_num, center_num, iter_num)
                    self.s.add(assigned_center_dist <= dist)
    
    def centers_correctly_updated(self):
        print("centers correctly updated")
        for iter_num in range(self.num_iters - 1):
            prev_iter = iter_num
            next_iter = iter_num + 1

            for center_num in range(self.num_centers):
                prev_x_points, prev_y_points = self.get_center_points(center_num, prev_iter)
                # cx_next, cy_next = self.centers_x[next_iter][center_num], self.centers_y[next_iter][center_num]
                cx_next, cy_next = Select(self.centers_x[next_iter], center_num), Select(self.centers_y[next_iter], center_num)
                self.s.add(cx_next * len(prev_x_points) == Sum(prev_x_points))
                self.s.add(cy_next * len(prev_y_points) == Sum(prev_y_points))
    
    def run(self):
        result = self.s.check()
        if result == sat:
            print("SATISFIABLE")
            px, py, cx, cy, pt_centers = self.evaluate_model_vars()
            # TODO: Need to create a visualization and call that here
            visualizer = Visualizer(self.num_iters, self.num_points, self.num_centers, self.grid_limit, px, py, cx, cy, pt_centers)
            visualizer.visualize()
        else:
            print("UNSATISFIABLE")
    
    def evaluate_model_vars(self):
        px, py = [], [] # x and y point coordinates (coordinate of i'th point at index i)
        for point_num in range(self.num_points):
            px.append(self.s.model().evaluate(self.points_x[point_num]))
            py.append(self.s.model().evaluate(self.points_y[point_num]))
        print("px:", px)
        print("py:", py)

        cx, cy = [], [] # i-th row: i-th iteration; j-th column: j-th center's coordinates
        for iter_num in range(self.num_iters):
            x_coords, y_coords = [], [] # coordinates for this iteration
            for center_num in range(self.num_centers):
                x_coords.append(self.s.model().evaluate(Select(self.centers_x[iter_num], center_num)))
                y_coords.append(self.s.model().evaluate(Select(self.centers_y[iter_num], center_num)))
            cx.append(x_coords)
            cy.append(y_coords)
        print("cx:", cx)
        print("cy:", cy)

        pt_centers = [] # i-th row: i-th iteration; j-th column: center_num for j-th point
        for iter_num in range(self.num_iters):
            iter_centers = []
            for point_num in range(self.num_points):
                iter_centers.append(self.s.model().evaluate(self.point_centers[iter_num][point_num]))
            pt_centers.append(iter_centers)
        print("pt_centers:", pt_centers)
        return px, py, cx, cy, pt_centers
    

    ##### HELPER FUNCTIONS #####

    def distance(self, point_num: int, center_num, iter_num: int):
        # returns the l1 (Manhattan) distance between a point and a center
        px, py = self.points_x[point_num], self.points_y[point_num]
        # cx, cy = self.centers_x[iter_num][center_num], self.centers_y[iter_num][center_num]
        cx, cy = Select(self.centers_x[iter_num], center_num), Select(self.centers_y[iter_num], center_num)

        return Abs(px - cx) + Abs(py - cy)

    # def get_min_dist_center(self, point_num: int, iter_num: int):
    #     distances = []
    #     for center_num in range(self.num_centers):
    #         distances.append(self.distance(point_num, center_num, iter_num))
    #     min_dist_center_num = Int(f"center_{point_num}_{iter_num}")
    #     self.s.add(min_dist_center_num < len(distances))
    #     self.s.add(min_dist_center_num >= 0)
    #     for center_num in range(self.num_centers):
    #         self.s.add(distances[self.center_var_to_center_num[iter_num][min_dist_center_num]] <= distances[center_num])
    #     return self.center_var_to_center_num[iter_num][min_dist_center_num]

    # def get_min_dist_center(self, point_num: int, iter_num: int):
    #     # returns the number of the center that is closest to the point with the provided point_num
    #     min_dist_center_num = None
    #     min_dist = None

    #     for center_num in range(self.num_centers):
    #         dist = self.distance(point_num, center_num, iter_num)
    #         # if (min_dist is None) or dist < min_dist:
    #         #     min_dist_center_num = center_num
    #         #     min_dist = dist
    #         if min_dist is None:
    #             min_dist_center_num = center_num
    #             min_dist = dist
    #         else:
    #             x = (dist < min_dist).is_true
    #             min_dist_center_num = If(dist < min_dist, center_num, min_dist_center_num)
    #             min_dist = If(dist < min_dist, dist, min_dist)
    #     ## MAYBE THIS FUNCTION SHOULD BE REWRITTEN TO GET ALL THE CENTERS, AND ASSERT THAT THE
    #     ## INT_VAL IT RETURNS IS THE ONE WITH THE SMALLEST VALUE
        
    #     return min_dist_center_num
    
    def get_center_points(self, center_num, iter_num: int):
        center_points_x = [] # x coordinates of points with this center
        center_points_y = [] # y coordinates of points with this center
        for point_num in range(self.num_points):
            pt_center_num = self.point_centers[iter_num][point_num]
            if pt_center_num == center_num:
                center_points_x.append(self.points_x[point_num])
                center_points_y.append(self.points_y[point_num])
        return center_points_x, center_points_y


def main(num_iters: int, num_points: int, num_centers: int, grid_limit: int):
    kmeans = KMeans(num_iters, num_points, num_centers, grid_limit)
    kmeans.run()
