# Import the required libraries.
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import networkx as nx

# Define the labels for cities.
cities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
numCities = len(cities)

# Define the cost matrix for travel between cities.
travelCost = [
    [0, 300, 450, 150, 225, 330, 495, 600, 315, 405],
    [300, 0, 180, 330, 315, 375, 510, 195, 420, 240],
    [450, 180, 0, 210, 495, 135, 240, 435, 180, 345],
    [150, 330, 210, 0, 360, 195, 300, 405, 270, 285],
    [225, 315, 495, 360, 0, 240, 465, 180, 285, 225],
    [330, 375, 135, 195, 240, 0, 270, 300, 345, 390],
    [495, 510, 240, 300, 465, 270, 0, 135, 255, 210],
    [600, 195, 435, 405, 180, 300, 135, 0, 285, 315],
    [315, 420, 180, 270, 285, 345, 255, 285, 0, 150],
    [405, 240, 345, 285, 225, 390, 210, 315, 150, 0]
]

# Define an array for benefit points.
benefitPoints = [350, 420, 270, 300, 380, 410, 320, 450, 330, 400]

# Create the model.
m = Model("Tan-Tech Investor Tour")

# Define the binary variables for travel routes.
x = m.addVars(numCities, numCities, vtype=GRB.BINARY, name="x")
y = m.addVars(numCities, vtype=GRB.BINARY, name="y")

# Define the objective function, which is to maximize the benefit points.
m.setObjective(quicksum(benefitPoints[i] * y[i] for i in range(numCities)), GRB.MAXIMIZE)

# Define the constraints of the problem.

# Constraint 1: The total travel cost cannot exceed 1500 USD.
m.addConstr(quicksum(travelCost[i][j] * x[i, j] for i in range(numCities) for j in range(numCities)) <= 1500, "Budget")

# Constraint 2: Due to logistical and team limitations, Tan-Tech can visit a maximum of 7 cities in total.
m.addConstr(quicksum(y[i] for i in range(numCities)) <= 7, "MaxCities")

# Constraint 3: The tour must start and end in City A.
m.addConstr(quicksum(x[0, j] for j in range(1, numCities)) == 1, "StartAtA")
m.addConstr(quicksum(x[i, 0] for i in range(1, numCities)) == 1, "EndAtA")

# Constraint 4: Flow constraints to ensure each visited city is entered and exited exactly once.
for i in range(1, numCities):
    m.addConstr(quicksum(x[i, j] for j in range(numCities) if j != i) == y[i], f"VisitOut_{i}")
    m.addConstr(quicksum(x[j, i] for j in range(numCities) if j != i) == y[i], f"VisitIn_{i}")

# Constraint 5: Subtour elimination (MTZ formulation).
u = m.addVars(numCities, vtype=GRB.INTEGER, name="u")
for i in range(1, numCities):
    for j in range(1, numCities):
        if i != j:
            m.addConstr(u[i] - u[j] + numCities * x[i, j] <= numCities - 1)

# Solve the model.
m.optimize()

# Output the results and prepare for plotting.
optimal_routes = []
visited_cities = set()
tour_benefits = []
tour_number = 1
if m.status == GRB.OPTIMAL:
    print("Optimal route found:")
    for i in range(numCities):
        for j in range(numCities):
            if x[i, j].x > 0.5:
                print(f"Travel from {cities[i]} to {cities[j]}")
                optimal_routes.append((cities[i], cities[j]))
                visited_cities.add(cities[i])
                visited_cities.add(cities[j])
                tour_benefits.append((tour_number, cities[i], benefitPoints[cities.index(cities[i])]))
                tour_number += 1
    print(f"Total Benefit Points: {m.objVal}")
else:
    print("No feasible solution found.")

# Plotting the optimal route.
if optimal_routes:
    G = nx.DiGraph()
    G.add_edges_from(optimal_routes)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, nodelist=list(visited_cities), node_size=700, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, edgelist=optimal_routes, arrowstyle='->', arrowsize=20, edge_color='black')
    nx.draw_networkx_labels(G, pos, labels={city: city for city in visited_cities}, font_size=12, font_color='black')
    plt.title('Optimal Tour for Tan-Tech Investor Tour')
    plt.show()

# Plotting the benefit points for each tour.
if tour_benefits:
    tour_numbers, cities_visited, benefits = zip(*tour_benefits)
    plt.figure(figsize=(12, 6))
    plt.bar(tour_numbers, benefits, color='skyblue')
    plt.xlabel('Tour Number')
    plt.ylabel('Benefit Points')
    plt.xticks(tour_numbers, cities_visited, rotation=45)
    plt.title('Benefit Points Obtained at Each Tour')
    plt.tight_layout()
    plt.show()
