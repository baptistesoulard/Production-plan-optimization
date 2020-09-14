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


def optimize_planning(
    timeline: List[str],
    workcenters: List[str],
    needs: Dict[str, int],
    wc_cost: Dict[str, int],
) -> pd.DataFrame:
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
        timeline,
        workcenters,
        lb=0,
        ub=12,
        vtype=gurobipy.GRB.INTEGER,
        name="Total hours",
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
    cost = model.addVars(
        timeline, workcenters, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="Cost"
    )

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
    optimization_var = gurobipy.quicksum(
        cost[(i, j)] for i in timeline for j in workcenters
    )
    objective = 0
    objective += optimization_var

    # SOLVE MODEL
    model.setObjective(objective)
    model.optimize()
    print("Total cost = $" + str(model.ObjVal))

    solution = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)
    solution = solution.iloc[2 * len(cost) : 3 * len(cost)]

    return solution


def plot_planning(planning: pd.DataFrame, needs: pd.DataFrame) -> None:
    planning = planning.T
    planning["Min capacity"] = 7
    planning["Max capacity"] = 12

    my_colors = ["skyblue", "salmon", "lightgreen"]

    fig, axs = plt.subplots(2)
    needs.T.plot(
        kind="bar",
        width=0.2,
        title="Need in h per day",
        ax=axs[0],
        color="midnightblue",
    )

    planning[["Min capacity", "Max capacity"]].plot(
        rot=90, ax=axs[1], style=["b", "b--"], linewidth=1
    )

    planning.drop(["Min capacity", "Max capacity"], axis=1).plot(
        kind="bar", title="Load in h per line", ax=axs[1], color=my_colors
    )

    axs[0].tick_params(axis="x", labelsize=7)
    axs[0].tick_params(axis="y", labelsize=7)
    axs[0].get_legend().remove()
    axs[0].set_xticklabels([])
    axs[1].tick_params(axis="x", labelsize=7)
    axs[1].tick_params(axis="y", labelsize=7)

    plt.savefig("Result_Model1.png", bbox_inches="tight", dpi=1200)
    plt.show()


# Generate inputs
# Define the daily requirement

daily_requirements: Dict[str, int] = {
    "2020/7/13": 30,
    "2020/7/14": 10,
    "2020/7/15": 34,
    "2020/7/16": 23,
    "2020/7/17": 23,
    "2020/7/18": 24,
    "2020/7/19": 25,
}

calendar: List[str] = list(daily_requirements.keys())
daily_requirements_df = pd.DataFrame.from_dict(daily_requirements)

# Define the hourly cost per line
costs_per_line = {"Curtain_C1": 350, "Curtain_C2": 300, "Curtain_C3": 350}
lines: List[str] = list(costs_per_line.keys())

# Optimize the planning
solution = optimize_planning(calendar, lines, daily_requirements, costs_per_line)

# Format the result
optimized_planning = pd.DataFrame(index=lines, columns=calendar)
for line in lines:
    for day in calendar:
        optimized_planning.at[line, day] = solution.loc[
            "Total hours[" + str(day) + "," + str(line) + "]"
        ][0]

# Plot the new planning
plot_planning(optimized_planning, daily_requirements_df)
