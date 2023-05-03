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

        def create_initial_x_centers(iter_num: int=0):
            cx = Array(f"cx_{iter_num}", IntSort(), IntSort())
            for center_num in range(self.num_centers):
                cx = Store(cx, center_num, Int(f"cx_{center_num}_{iter_num}"))
            return cx
        def create_initial_y_centers(iter_num: int=0):
            cy = Array(f"cy_{iter_num}", IntSort(), IntSort())
            for center_num in range(self.num_centers):
                cy = Store(cy, center_num, Int(f"cy_{center_num}_{iter_num}"))
            return cy

        # self.centers_x = {iter_num: create_x_centers() for iter_num in range(self.num_iters)}
        self.centers_x = {0: create_initial_x_centers()} 
        # self.centers_y = {iter_num: create_y_centers(iter_num) for iter_num in range(self.num_iters)}
        self.centers_y = {0: create_initial_y_centers()}

        # center for some point
        def create_point_centers(iter_num: int):
            return {i: Int(f"center_{i}_{iter_num}") for i in range(num_points)}
        self.point_centers = {iter_num: create_point_centers(iter_num) for iter_num in range(self.num_iters)}
        # Each point is mapped to an int which we will constrain such that it is equal to the key
        # corresponding to the center that is closest to the point

        ## Enforcing constraints that should always be true:
        self.create_model()


    ##### FUNCTIONS ENFORCING CONSTRAINTS ON SOLVER VARIABLES #####
    
    def points_within_grid(self):
        """
        Ensures that all of the datapoints lie within the bounds of the defined grid
        """
        print("points within grid")
        for i in range(self.num_points):
            self.s.add(And(self.points_x[i] >= -self.grid_limit, self.points_x[i] <= self.grid_limit))
            self.s.add(And(self.points_y[i] >= -self.grid_limit, self.points_y[i] <= self.grid_limit))
    
    def no_duplicate_points(self):
        """
        Ensures that there are no duplicated datapoints (all datapoints should be unique)
        """
        print("no duplicate points")
        for i in range(self.num_points):
            for j in range(i+1, self.num_points, 1):
                px1, py1 = self.points_x[i], self.points_y[i]
                px2, py2 = self.points_x[j], self.points_y[j]
                self.s.add(Or(px1 != px2, py1 != py2))
    
    def centers_within_grid(self, iter_num: int):
        """
        Ensures that all cluster centers (for the specified iteration number) lie within the bounds
        of the defined grid.
        params:
            iter_num: which iteration we are checking for
        """
        print("centers within grid")
        # for iter_num in range(self.num_iters):
        for i in range(self.num_centers):
            self.s.add(And(Select(self.centers_x[iter_num], i) >= -self.grid_limit, Select(self.centers_x[iter_num], i) <= self.grid_limit))
            self.s.add(And(Select(self.centers_y[iter_num], i) >= -self.grid_limit, Select(self.centers_y[iter_num], i) <= self.grid_limit))
    
    def point_centers_are_valid_center_numbers(self, iter_num: int):
        """
        Ensures that the center numbers assigned to each point (depicting which center is closest
        to the point, and therefore, which center/cluster the point is assigned to) in the
        specified iteration is a valid center num (between 0 and self.num_centers - 1, inclusive).
        params:
            iter_num: which iteration we are checking for
        """
        print("point centers are valid center numbers")
        # for iter_num in range(self.num_iters):
        for i in range(self.num_points):
            center_var = self.point_centers[iter_num][i]
            self.s.add(And(center_var >= 0, center_var < self.num_centers))
    
    def points_have_closest_center(self, iter_num: int):
        """
        Ensures that the center assigned to each point (in the specified iteration) is the center
        that is closest to it.
        params:
            iter_num: which iteration we are checking for
        """
        print("points have closest center")
        # for iter_num in range(self.num_iters):
        for point_num in range(self.num_points):
            center_num_var = self.point_centers[iter_num][point_num]
            assigned_center_dist = self.distance(point_num, center_num_var, iter_num)
            for center_num in range(self.num_centers):
                dist = self.distance(point_num, center_num, iter_num)
                self.s.add(assigned_center_dist <= dist)

    def create_model(self):
        """
        Constructs model constraints across all iterations
        """
        ## Independent of iterations:
        self.points_within_grid() # All points are within the grid
        self.no_duplicate_points() # No points are duplicates

        ## Iteration specific properties:
        for iter_num in range(self.num_iters):
            self.centers_within_grid(iter_num) # All centers are within the grid
            self.point_centers_are_valid_center_numbers(iter_num)
            self.points_have_closest_center(iter_num)
            # self.overlap_centers(iter_num)
            temp_result = self.s.check()
            if temp_result == sat:

                ### Assigning the centers for the next iteration ###
                # 1. extract point centers for this iteration
                pt_centers = {center_num: [] for center_num in range(self.num_centers)}
                for point_num in range(self.num_points):
                    center_num = self.s.model().evaluate(self.point_centers[iter_num][point_num])
                    center_num = int(center_num.as_string())
                    assert (center_num in pt_centers) # shouldn't be an invalid center_num
                    pt_centers[center_num].append(point_num)
                
                # 2. extracting point x and y coordinates
                if iter_num == 0:
                    px, py = [], []
                    for point_num in range(self.num_points):
                        x = self.s.model().evaluate(self.points_x[point_num])
                        px.append(int(x.as_string()))
                        y = self.s.model().evaluate(self.points_y[point_num])
                        py.append(int(y.as_string()))
                    self.points_x = {point_num: px[point_num] for point_num in range(self.num_points)}
                    self.points_y = {point_num: py[point_num] for point_num in range(self.num_points)}
                else:
                    px, py = list(self.points_x.values()), list(self.points_y.values())
                
                # 3. compute new center values
                cx, cy = [], []
                for center_num in range(self.num_centers):
                    n = len(pt_centers[center_num])
                    if n == 0: # keep the center in the same position
                        x = self.s.model().evaluate(Select(self.centers_x[iter_num], center_num))
                        cx.append(int(x.as_string()))
                        y = self.s.model().evaluate(Select(self.centers_y[iter_num], center_num))
                        cy.append(int(y.as_string()))
                    else: # new center values based on point averages
                        x_coords = [px[pt_num] for pt_num in pt_centers[center_num]]
                        y_coords = [py[pt_num] for pt_num in pt_centers[center_num]]
                        cx.append(sum(x_coords) // n)
                        cy.append(sum(y_coords) // n)
                
                # storing the values for iteration 0 centers 
                # so that z3 doesn't 're-evaluate' in a manner that becomes inconsistent with the final result
                # which was happening when they were stored as z3 centers
                if iter_num == 0:
                    center_x = Array(f"cx_{iter_num}", IntSort(), IntSort())
                    center_y = Array(f"cy_{iter_num}", IntSort(), IntSort())
                    for center_num in range(self.num_centers):
                        x = self.s.model().evaluate(Select(self.centers_x[iter_num], center_num))
                        center_x = Store(center_x, center_num, int(x.as_string()))
                        y = self.s.model().evaluate(Select(self.centers_y[iter_num], center_num))
                        center_y = Store(center_y, center_num, int(y.as_string()))
                    self.centers_x[iter_num] = center_x
                    self.centers_y[iter_num] = center_y


                # 4. update the values of self.centers_x and self.centers_y
                center_x = Array(f"cx_{iter_num+1}", IntSort(), IntSort())
                center_y = Array(f"cy_{iter_num+1}", IntSort(), IntSort())
                for center_num in range(self.num_centers):
                    center_x = Store(center_x, center_num, cx[center_num])
                    center_y = Store(center_y, center_num, cy[center_num])
                self.centers_x[iter_num+1] = center_x
                self.centers_y[iter_num+1] = center_y
            else:
                raise Exception("Impossible instance: UNSAT at an intermediate step!")
    
    def run(self):
        """
        Runs the model whose constraints have been defined by previously calling the create_model
        function. Checks if the result is satisfiable; if it is, evaluates model variables and
        runs the visualization script.
        """
        result = self.s.check()
        if result == sat:
            print("SATISFIABLE")
            px, py, cx, cy, pt_centers = self.evaluate_model_vars()
            # Visualize instance:
            visualizer = Visualizer(self.num_iters, self.num_points, self.num_centers, self.grid_limit, px, py, cx, cy, pt_centers)
            visualizer.visualize()
        else:
            print("UNSATISFIABLE")
    
    def evaluate_model_vars(self):
        """
        Evaluates the model's variables: evaluates all the z3 variables associated with some satisfiable
        instance and organizes values into datastructures that can be fed into the visualization script
        """
        px, py = list(self.points_x.values()), list(self.points_y.values())
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
        """
        Computes the l1 (Manhattan) distance between the point with the provided point number
        and the center with the provided center num (based on their positions in the specified
        iteration).
        params:
            point_num: the number of the point whose coordinates should be considered
            center_num: the number of the center whose coordinates should be considered
            iter_num: which iteration we are checking for 
        """
        # returns the l1 (Manhattan) distance between a point and a center
        px, py = self.points_x[point_num], self.points_y[point_num]
        cx, cy = Select(self.centers_x[iter_num], center_num), Select(self.centers_y[iter_num], center_num)

        return Abs(px - cx) + Abs(py - cy)


    ##### PROPERTY VERIFICATION FUNCTIONS #####
    # TODO: Define funcntions that add constraints for specific property verifications
    # NOTE: Remember to use .push() and .pop() when defining these property-specific constraints
    def overlap_centers(self, iter_num: int):
        i, j = Ints('i j')
        self.s.add(And(i >= 0, i < self.num_centers))
        self.s.add(And(j >= 0, j < self.num_centers))
        self.s.add(i != j)

        self.s.add(Exists([i, j], And(Select(self.centers_x[iter_num], i) == Select(self.centers_x[iter_num], j), 
                                      Select(self.centers_y[iter_num], i) == Select(self.centers_y[iter_num], j))))


def main(num_iters: int, num_points: int, num_centers: int, grid_limit: int):
    """
    main function that intantiates an object of the KMeans class and then runs the model.
    params:
        num_iters: number of iterations for which to run the algorithm
        num_points: number of datapoints
        num_centers: number of centers
        grid_limit: dimensions of the grid (ex: if the grid_limit is 5, then the coordinates go from
                                            -5.0 to 5.0 along both axes)
    """
    kmeans = KMeans(num_iters, num_points, num_centers, grid_limit)
    kmeans.run()

