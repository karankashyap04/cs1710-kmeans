#lang forge

option problem_type temporal

-- NOTE: need a bitwidth of 8

sig Number {
    digit: one Int,
    decimal: one Int
}

sig Coordinate {
    x: one Number,
    y: one Number
}

sig Center {
    var coordinate: one Coordinate
}
    
sig Point {
    coordinate: one Coordinate,
    -- center is lone because in first state, points are not assigned to a center
    var center: lone Center
}

-- need to make sure that this is always true for purposes of squared distance remaining within integer bitwidth
pred numberWellformed {
    all n: Number | {
        n.digit <= 2 and n.digit >= -2
        (n.digit = 2 or n.digit = -2) implies n.decimal = 0
    }
}

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


Functions (not predicates) that we might want:
- multiply --> takes in two Numbers and give us their product
    - can we store variables (let expressions?)
- distance --> takes 2 coordinates and returns the distance between them
- getCenter --> takes a point and returns the center which is closest to it