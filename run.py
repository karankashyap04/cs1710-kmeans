import argparse

from kmeans import main

if __name__ == '__main__':
    """
    main function that can be called from the terminal. Sets up the argparse and calls the main()
    function in kmeans.py
    """
    parser = argparse.ArgumentParser("SMT solver: Property Verifications of the k-Means Clustering Algorithm")

    parser.add_argument("-i", "--num_iters", default=5, type=int, help="Number of iterations for which to run the algorithm")
    parser.add_argument("-p", "--num_points", default=10, type=int, help="Number of datapoints to generate")
    parser.add_argument("-c", "--num_centers", default=3, type=int, help="Number of clusters (and therefore, the number of cluster centers)")
    parser.add_argument("-g", "--grid_limit", default=5, type=int, help="board dimension (each axis goes from -grid_limit to grid_limit)")
    parser.add_argument("--random_centers", default=False, action="store_true",
                        help="flag indicating whether or not to random initialize centers")

    args = parser.parse_args()
    num_iters = args.num_iters
    num_points = args.num_points
    num_centers = args.num_centers
    grid_limit = args.grid_limit
    random_centers = args.random_centers

    main(num_iters, num_points, num_centers, grid_limit, random_centers)
