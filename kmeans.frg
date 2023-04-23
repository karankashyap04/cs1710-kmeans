#lang forge

option problem_type temporal

-- NOTE: need a bitwidth of 8

sig Coordinate {
    x: one Int,
    y: one Int
}

sig Center {
    var coord: one Coordinate
}
    
sig Point {
    coordinate: one Coordinate,
    -- center is lone because in first state, points are not assigned to a center
    var center: lone Center
}

one sig Iteration {
    n: one Int, -- total number of iterations to perform
    var i: one Int -- current iteration we are on
}
-- NOTE: once i reaches n, enforce doNothing predicate! (doNothing iff i = n)

-----------------------------------------------

-- Returns the l1 (Manhattan) distance between 2 points
fun distance[p: Point, c: Center]: Int {
    add[abs[p.coordinate.x - c.coord.x], abs[p.coordinate.y - c.coord.y]]
}

fun meanX[c: Center]: Int {
    -- get all the points with the center
    let points = {p: Point | p.center = c} | {
        let xVals = points.coordinate.x | {
            let n = #points | {
                remainder[sum[xVals], n] < 5 implies {
                     -- rounding
                    divide[sum[xVals], n] + 1
                }
                else {divide[sum[xVals], n]}
            }
        }
    }
}

fun meanY[c: Center]: Int {
    -- get all the points with the center
    let points = {p: Point | p.center = c} | {
        let yVals = points.coordinate.y | {
            let n = #points | {
                remainder[sum[yVals], n] < 5 implies {
                     -- rounding
                    add[divide[sum[yVals], n] , 1]
                }
                else {divide[sum[yVals], n]}
            }
        }
    }
}

-----------------------------------------------


pred coordinatesWellformed {
    -- rationale: if we have a bitwidth of 8, we can go from -128 to 127. With a grid from -30 to
    --            30 along both axes, the max manhattan distance we can have is 60 along x and 60
    --            along y, making the total 120, which is right under the bitwidth constraint
    all c: coordinate | {
        c.x >= -30
        c.x <= 30
        c.y >= -30
        c.y <= 30
    }
}


pred checkCenter[p: Point] {
    -- no center should be closer to p than p.center
    let pCenterDist = distance[p, p.center] | {
        all c: {Center - p.center} | distance[p, c] > pCenterDist
    }
}

pred init {
    no p: Point | some p.center -- no pointer should have a center
    Iteration.i = 0 -- no iterations completed yet
}

pred assignCenters {
    -- center should be the one whose distance is the least
    all p: Point | some p.center'
    all p: Point | next_state checkCenter[p]
}

pred calculateCenters {
    -- next state center should be the mean of all the ones that have it in this state
    all c: Center | {
        next_state {c.coord.x = meanX[c]}
        next_state {c.coord.y = meanY[c]}
    }
}

pred doNothing {
    Point.center = Point.center'
    Center.coordinate = Center.coordinate'
    Iteration.i = Iteration.i'
}

pred transitions {
    init
    always {coordinatesWellformed}
    always {
        (i < n) implies {
            Iteration.i' = add[Iteration.i, 1]
            assignCenters
            calculateCenters
        } else {
            -- doNothing predicate here
        }
    }
}

-----------------------------------------------

run {
    Iteration.n = 5
    transitions
} for exactly 20 Point, exactly 2 Center

// Sigs that we might want:
// - Coordinate --> represents a single coordinate (currently, in 2 dimensional space)
//     - x: one Int
//     - y: one Int
//     QUESTION: is there something we could do to make the number of dimensions variable?
// - Center --> cluster to represent the center of each cluster (controlling the number of Centers would be how we could control how many clusters we segment the data into)
//     - coordinate: one Coordinate
// - Point --> represents a datapoint that we want to cluster (via the algorithm)
//     - coordinate: one Coordinate
//     - center: lone Center


// Functions (not predicates) that we might want:
// - product --> takes in two Numbers and give us their product
//     - can we store variables (let expressions?)
//     - we would need to do casework for decimal * decimal, decimal * digit in order to sum up the parts
// - plus --> takes in two Numbers and give us their sum
// - distance --> takes 2 coordinates and returns the distance between them
// - compare --> takes two Numbers and checks if the first is greater than the second
// - quotient --> takes two Numbers and gives us their quotient
// - avgCoordinate --> takes in center (because we can then find all the points that have that center) and gives us a new coordinate for that center


// Predicates:
// getCenter --> takes a point and ensures that its the center which is closest to it
// transition --> 

// discuss:
// new properties (property verification)
// implementing our own arithmetic 
// transition predicate (how do we separate point assignment and center reassignment while still enforcing the order)
-- either way works really (if we want to do them together, use the idea of next_state points -- next_state points depends on current state centers; next_state centers depends on next_state points)

// use partial instance (constraints) to constrain n for Iteration
