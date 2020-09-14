# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:09:01 2020

@author: soulba01
"""

# Import required packages
import pandas as pd
import gurobipy
from matplotlib import pyplot as plt
from typing import List, Dict


def optimize_planning(timeline, workcenters, needs, wc_cost):
    # Initiate optimization model
    model = gurobipy.Model("Optimize production planning")

    # DEFINE VARIABLES
    # Define time variables
    hours = model.addVars(
        timeline, workcenters, lb=7, ub=12, vtype=gurobipy.GRB.INTEGER, name="Hours"
    )
    line_opening = model.addVars(
        timeline, workcenters, vtype=gurobipy.GRB.BINARY, name="Line opening"
    )
    total_hours = model.addVars(
        timeline, workcenters, lb=0, ub=12, vtype=gurobipy.GRB.INTEGER, name="Total hours"
    )

    model.addConstrs(
        (
            (
                total_hours[(i, j)] == hours[(i, j)] * line_opening[(i, j)]
                for i in timeline
                for j in workcenters
            )
        ),
        name="total_hours_constr",
    )

    # Define cost variable
    cost = model.addVars(timeline, workcenters, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="Cost")

    model.addConstrs(
        (
            (
                cost[(i, j)] == total_hours[(i, j)] * wc_cost[j]
                for i in timeline
                for j in workcenters
            )
        )
    )

    # CONSTRAINTS
    # Total requirement = total planned
    model.addConstrs(
        (total_hours.sum(d, "*") == needs[d] for d in timeline),
        name="Requirements",
    )

    # DEFINE MODEL
    # Objective : minimize a function
    model.ModelSense = gurobipy.GRB.MINIMIZE
    # Function to minimize
    optimization_var = gurobipy.quicksum(cost[(i, j)] for i in timeline for j in workcenters)
    objective = 0
    objective += optimization_var

    # SOLVE MODEL
    model.setObjective(objective)
    model.optimize()
    print("Total cost = $" + str(model.ObjVal))

    sol = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)
    sol = sol.iloc[2 * len(cost): 3 * len(cost)]

    return sol


def plot_planning(plan, need):
    plan = plan.T
    plan["Min capacity"] = 7
    plan["Max capacity"] = 12

    my_colors = ["skyblue", "salmon", "lightgreen"]

    fig, axs = plt.subplots(2)
    need.T.plot(
        kind="bar", width=0.2, title="Need in h per day", ax=axs[0], color='midnightblue'
    )

    plan[["Min capacity", "Max capacity"]].plot(
        rot=90, ax=axs[1], style=["b", "b--"], linewidth=1
    )

    plan.drop(["Min capacity", "Max capacity"], axis=1).plot(
        kind="bar", title="Load in h per line", ax=axs[1], color=my_colors
    )

    axs[0].tick_params(axis="x", labelsize=7)
    axs[0].tick_params(axis="y", labelsize=7)
    axs[0].get_legend().remove()
    axs[0].set_xticklabels([])
    axs[1].tick_params(axis="x", labelsize=7)
    axs[1].tick_params(axis="y", labelsize=7)

    plt.savefig("Result_Model1.png", bbox_inches="tight", dpi=1200)
    axe = plt.show()
    return axe


# Generate inputs
# Define the daily requirement
CALENDAR: List[str] = [
    "2020/7/13",
    "2020/7/14",
    "2020/7/15",
    "2020/7/16",
    "2020/7/17",
    "2020/7/18",
    "2020/7/19",
]
day_req: List[int] = [30, 10, 34, 23, 23, 24, 25]
DAY_REQUIREMENTS: Dict[str, int] = {day: day_req[i] for i, day in enumerate(CALENDAR)}
df_requirement = pd.DataFrame.from_dict({day: [day_req[i]] for i, day in enumerate(CALENDAR)})

# Define the hourly cost per line
LINES: List[str] = ["Curtain_C1", "Curtain_C2", "Curtain_C3"]
cost_temp: List[int] = [350, 300, 350]
COST_LINE = {line: cost_temp[i] for i, line in enumerate(LINES)}

# Optimize the planning
solution = optimize_planning(CALENDAR, LINES, DAY_REQUIREMENTS, COST_LINE)

# Format the result
optimized_planning = pd.DataFrame(index=LINES, columns=CALENDAR)
for line in LINES:
    for day in CALENDAR:
        optimized_planning.at[line, day] = solution.loc["Total hours[" + str(day) + "," + str(line) + "]"][0]

# Plot the new planning
plot_planning(optimized_planning, df_requirement)
