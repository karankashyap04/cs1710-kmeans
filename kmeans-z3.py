from z3 import *

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

        # Grid of defined coordinates
        # self.defined_coordinates = [(i, j) for j in range(-grid_limit, grid_limit + 1) for i in range(-grid_limit, grid_limit + 1)]

        # Grid variables
        # self.grid = {(i, j): Ints(f"var_{i}_{j}") for i in range(-grid_limit, grid_limit+1) for j in range(-grid_limit, grid_limit + 1)}

        self.points_x = {i: Ints(f"px_{i}") for i in range(self.num_points)}
        self.points_y = {i: Ints(f"py_{i}") for i in range(self.num_points)}

        self.centers_x = {i: Ints(f"cx_{i}") for i in range(self.num_centers)}
        self.centers_y = {i: Ints(f"cy_{i}") for i in range(self.num_centers)}

        # center for some point
        self.point_centers = {i: Ints(f"center_{i}") for i in range(num_points)}
        # Each point is mapped to an int which we will constrain such that it is equal to the key
        # corresponding to the center that is closest to the point

        # This dictionary will help us reverse index so we can go from the z3 variable to the int
        # which will allow us to key into the centers_x and centers_y hashmaps (or just provide
        # the center number for the distance function)
        self.center_var_to_center_num = {self.points_centers[i]: i for i in range(num_points)}


        ## Enforcing constraints that should always be true:
        self.points_within_grid()
        self.centers_within_grid()


    ##### FUNCTIONS ENFORCING CONSTRAINTS ON SOLVER VARIABLES #####
    
    def points_within_grid(self): # Ensures that all points are within the defined grid
        for i in range(self.num_points):
            self.s.add(And(self.points_x[i] >= -self.grid_limit, self.points_x[i] <= self.grid_limit))
            self.s.add(And(self.points_y[i] >= -self.grid_limit, self.points_y[i] <= self.grid_limit))
    
    def centers_within_grid(self): # Ensures that all centers are within the defined grid
        for i in range(self.num_centers):
            self.s.add(And(self.centers_x[i] >= -self.grid_limit, self.centers_x[i] <= self.grid_limit))
            self.s.add(And(self.centers_y[i] >= -self.grid_limit, self.centers_y[i] <= self.grid_limit))
    
    def points_have_closest_center(self):
        self.s.push()
        for point_num in range(self.num_points):
            expected_center_num = self.get_min_dist_center(point_num)
            center_var = self.point_centers[point_num]
            self.s.add(self.center_var_to_center_num[center_var] == expected_center_num)
        self.s.pop()
    

    ##### HELPER FUNCTIONS #####

    def distance(self, point_num: int, center_num: int):
        # returns the l1 (Manhattan) distance between a point and a center
        px, py = self.points_x[point_num], self.points_y[point_num]
        cx, cy = self.centers_x[center_num], self.centers_y[center_num]

        return Abs(px - cx) + Abs(py - cy)

    def get_min_dist_center(self, point_num: int):
        # returns the number of the center that is closest to the point with the provided point_num
        min_dist_center_num = None
        min_dist = None

        for center_num in range(self.num_centers):
            dist = self.distance(point_num, center_num)
            if (min_dist is None) or dist < min_dist:
                min_dist_center_num = center_num
                min_dist = dist
        
        return min_dist_center_num
