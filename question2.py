import time
import gurobipy as gp
from gurobipy import GRB

items_data = [
    (2, 300, 5, "Granola Bars"),
    (1, 800, 10, "Trail Mix"),
    (2, 200, 4, "Dried Fruit"),
    (6, 800, 7, "Canned Beans"),
    (4, 1100, 8, "Rice"),
    (6, 150, 3, "Energy Drink"),
    (5, 1200, 9, "Pasta"),
    (2, 500, 6, "Jerky")
]

REQUIRED_CALORIES = 3500
CAPACITY_ECE = 10
CAPACITY_ARDA = 8

best_cost_BNB = float('inf')
best_solution_BNB = None

max_cal_suffix = [0] * len(items_data)
running_sum = 0
for i in reversed(range(len(items_data))):
    running_sum += items_data[i][1]
    max_cal_suffix[i] = running_sum


def branch_and_bound_2subset_knapsack(
        index,
        ece_weight,
        arda_weight,
        total_calories,
        total_cost,
        selected_items
):
    global best_cost_BNB, best_solution_BNB

    # Prune if capacity exceeded
    if ece_weight > CAPACITY_ECE or arda_weight > CAPACITY_ARDA:
        return

    # Prune if cost already worse than best
    if total_cost >= best_cost_BNB:
        return

    if index == len(items_data):
        # Reached a leaf node; check calorie requirement
        if total_calories >= REQUIRED_CALORIES:
            if total_cost < best_cost_BNB:
                best_cost_BNB = total_cost
                best_solution_BNB = selected_items[:]
        return

    # Bound: if even taking all remaining items can't hit 3500 calories, prune
    potential_max_cal = total_calories + max_cal_suffix[index]
    if potential_max_cal < REQUIRED_CALORIES:
        return

    w_i, cal_i, cost_i, name_i = items_data[index]

    # BRANCH 1: NOT CHOSEN
    selected_items.append(0)
    branch_and_bound_2subset_knapsack(
        index + 1,
        ece_weight,
        arda_weight,
        total_calories,
        total_cost,
        selected_items
    )
    selected_items.pop()

    # BRANCH 2: CHOSEN BY ECE
    selected_items.append(1)
    branch_and_bound_2subset_knapsack(
        index + 1,
        ece_weight + w_i,
        arda_weight,
        total_calories + cal_i,
        total_cost + cost_i,
        selected_items
    )
    selected_items.pop()

    # BRANCH 3: CHOSEN BY ARDA
    selected_items.append(2)
    branch_and_bound_2subset_knapsack(
        index + 1,
        ece_weight,
        arda_weight + w_i,
        total_calories + cal_i,
        total_cost + cost_i,
        selected_items
    )
    selected_items.pop()


def solve_custom_BNB():
    global best_cost_BNB, best_solution_BNB
    best_cost_BNB = float('inf')
    best_solution_BNB = None

    branch_and_bound_2subset_knapsack(
        index=0,
        ece_weight=0,
        arda_weight=0,
        total_calories=0,
        total_cost=0,
        selected_items=[]
    )
    return best_cost_BNB, best_solution_BNB


def print_BNB_solution(cost, solution):
    if solution is None:
        print("No feasible B&B solution found.")
        return
    print(f"B&B: Found best cost = {cost}")
    ece_list = []
    arda_list = []
    total_cals = 0
    total_w_ece = 0
    total_w_arda = 0

    for i, assign in enumerate(solution):
        w_i, cal_i, cost_i, name_i = items_data[i]
        if assign == 1:
            ece_list.append(name_i)
            total_w_ece += w_i
            total_cals += cal_i
        elif assign == 2:
            arda_list.append(name_i)
            total_w_arda += w_i
            total_cals += cal_i

    print(f"  Ece carries: {ece_list} (Weight={total_w_ece} kg)")
    print(f"  Arda carries: {arda_list} (Weight={total_w_arda} kg)")
    print(f"  Combined calories = {total_cals} (≥ {REQUIRED_CALORIES})")

def solve_with_gurobi():



    n = len(items_data)
    w = [items_data[i][0] for i in range(n)]
    cal = [items_data[i][1] for i in range(n)]
    cost = [items_data[i][2] for i in range(n)]

    m = gp.Model("MealPlan2SubsetKnapsack")

    x = m.addVars(n, vtype=GRB.BINARY, name="x")
    y = m.addVars(n, vtype=GRB.BINARY, name="y")

    # Objective
    m.setObjective(gp.quicksum(cost[i] * x[i] for i in range(n)), GRB.MINIMIZE)

    # Constraint: total calories >= 3500
    m.addConstr(gp.quicksum(cal[i] * x[i] for i in range(n)) >= REQUIRED_CALORIES, name="CalReq")

    # Ece capacity
    m.addConstr(gp.quicksum(w[i] * y[i] for i in range(n)) <= CAPACITY_ECE, name="EceCap")

    # Arda capacity
    m.addConstr(gp.quicksum(w[i] * (x[i] - y[i]) for i in range(n)) <= CAPACITY_ARDA, name="ArdaCap")

    # Logical link: y[i] <= x[i]
    for i in range(n):
        m.addConstr(y[i] <= x[i], name=f"logic_{i}")

    # Solve
    m.setParam("OutputFlag", 0)  # silent
    m.optimize()

    if m.status == GRB.OPTIMAL:
        xSol = [int(round(x[i].X)) for i in range(n)]
        ySol = [int(round(y[i].X)) for i in range(n)]
        return m.objVal, (xSol, ySol)
    else:
        return None, (None, None)


def print_gurobi_solution(cost, xSol, ySol):

    if cost is None or xSol is None:
        print("No feasible Gurobi solution found.")
        return
    print(f"Gurobi: Found best cost = {cost}")
    ece_list = []
    arda_list = []
    total_cals = 0
    total_w_ece = 0
    total_w_arda = 0

    for i in range(len(items_data)):
        w_i, cal_i, cost_i, name_i = items_data[i]
        if xSol[i] == 1:
            # item is chosen, check who carries it
            if ySol[i] == 1:
                # carried by Ece
                ece_list.append(name_i)
                total_w_ece += w_i
                total_cals += cal_i
            else:
                # carried by Arda
                arda_list.append(name_i)
                total_w_arda += w_i
                total_cals += cal_i

    print(f"  Ece carries: {ece_list} (Weight={total_w_ece} kg)")
    print(f"  Arda carries: {arda_list} (Weight={total_w_arda} kg)")
    print(f"  Combined calories = {total_cals} (≥ {REQUIRED_CALORIES})")


def main():
    start_bnb = time.time()
    cost_bnb, sol_bnb = solve_custom_BNB()
    end_bnb = time.time()

    print_BNB_solution(cost_bnb, sol_bnb)
    bnb_time = end_bnb - start_bnb
    print(f"B&B runtime = {bnb_time:.6f} seconds\n")


    start_gurobi = time.time()
    cost_gurobi, (xSol, ySol) = solve_with_gurobi()
    end_gurobi = time.time()

    print_gurobi_solution(cost_gurobi, xSol, ySol)
    gurobi_time = end_gurobi - start_gurobi
    print(f"Gurobi runtime = {gurobi_time:.6f} seconds\n")


    print("=== Comparison Summary ===")
    print(f" B&B cost = {cost_bnb}, runtime = {bnb_time:.6f} s")
    print(f" Gurobi cost = {cost_gurobi}, runtime = {gurobi_time:.6f} s")
    print("Note: Both should ideally yield the same minimal cost (if optimal).")


if __name__ == "__main__":
    main()
