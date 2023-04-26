import matplotlib.pyplot as plt
from typing import List

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
    
    def visualize(self):
        pass