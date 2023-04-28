# Note on Visualizations

As of now (_note: this might be changed in the future_), the sample visualizations in this directory are in the format of PDF files. It is important to note that the visualization produced by the code in `visualizer.py` does not produce this PDF. The code in this file produces individual graph plots: one for each iteration. As of now, we are manually taking these plot images and compiling them into PDFs for ease of keeping track of them and viewing them together.

## File naming conventions:
Here is an explanation of the naming convention being used for the visualization files as of now:
For some instance that we are running, let:
- `num_iters`: number of iterations
- `num_points`: number of datapoints
- `num_centers`: number of centers (number of clusters)
- `grid_limit`: grid limit (how far, on each of the 4 cardinal directions from the origin we define our space until

The visualization file's name for this instance would be: `i<num_iters>_p<num_points>_c<num_centers>_g<grid_limit>.pdf` (where each of the variables placed withi angular brackets `<>` are replaced with their numerical value).
