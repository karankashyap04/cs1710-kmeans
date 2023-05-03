# cs1710-kmeans
Final project for CS1710: Modeling the k-means clustering algorithm

**Note:** When we have our final demo with Tim, he mentioned that we should make sure to remind him of our desire to potentially make animations, regardless of whether or not we actually land up needing them... he said he wants to be reminded of that as a potential extension of Sterling visualizationns (through a `d3` library or something like that).

**Meeting 2 Notes:** 
- We are having issues with Property Verification because our algorithm uses 'manually calculated' centers (which Tim said we would have to do), meaning they are no longer Z3 variables so we cannot add constraints to the system in order to 'search the space'... we have one idea for a property relating to points which we believe we could verify but it's not that good
- Soundness and Completeness: need a little bit more direction in terms of soundness, not quite sure how to do completeness without just copying the code we're already using (for example, when ensuring points are with the correct centers, we need to somehow know information about the correct center which we would do by comparing distances but that's exactly what we do within the model)
