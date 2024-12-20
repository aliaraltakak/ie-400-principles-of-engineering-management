# IE400 Principles of Engineering Management - Term Project

This repository contains the implementation and solution for the term project of the IE400 Principles of Engineering Management course. The project includes solving two optimization problems using Python and related libraries.

## Project Overview

The project involves two distinct problems:

### Question 1: Promotional Tour Optimization
A tech startup, Tan-Tech, plans a promotional tour across multiple cities to maximize exposure within budget and time constraints. The optimization problem focuses on:

- Maximizing benefit points for selected cities.
- Ensuring the total travel cost does not exceed $1,500.
- Visiting a maximum of 7 cities, starting and ending at city A.

**Approach:**
We use Gurobi, an optimization solver, to formulate and solve the problem.

### Question 2: Balanced Meal Plan for a Hiking Trip
Ece and Arda aim to select food items for a hiking trip, balancing calorie needs, backpack weight constraints, and cost minimization.

**Problem Details:**
- Binary Integer Programming is used to select items.
- Constraints include:
  - Backpack weight limits for Ece (10 kg) and Arda (8 kg).
  - Minimum calorie intake for Ece (2,000 calories) and Arda (1,500 calories).
  - Only one of each type of food item can be included.

**Approach:**
A branch-and-bound algorithm is implemented and compared with Gurobi for performance.

## Files in the Repository

### 1. [IE400ProjectDescription.pdf](IE400ProjectDescription.pdf)
Contains the detailed description of the project and problem requirements.

### 2. [question1.py](question1.py)
Python script for solving the promotional tour optimization problem. The script includes:
- Problem formulation using Gurobi.
- Code for generating the optimal route.

### 3. [question2.py](question2.py)
Python script for solving the balanced meal plan problem. The script includes:
- Implementation of the branch-and-bound algorithm.
- Comparison of results with Gurobi.

## Output

Each script generates outputs based on the optimization problem:
- **Question 1:** Optimal city route with total cost and benefit points.
- **Question 2:** Optimal meal plan with selected items, total weight, and calorie intake.

