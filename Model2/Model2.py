# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:09:01 2020

@author: soulba01
"""

# Import required packages
import pandas as pd
import gurobipy
from matplotlib import pyplot as plt
import datetime


def optimize_planning(timeline, workcenters, needs, wc_cost_reg, wc_cost_ot):
    # Initiate optimization model
    model = gurobipy.Model("Minimize cost")

    # DEFINE VARIABLES
    # Load variables (hours) - regular and overtime
    reg_hours = model.addVars(
        timeline, workcenters, lb=7, ub=8, vtype=gurobipy.GRB.INTEGER, name="Regular hours"
    )
    ot_hours = model.addVars(
        timeline, workcenters, lb=0, ub=4, vtype=gurobipy.GRB.INTEGER, name="OT hours"
    )
    # Status of the line ( 0 = closed, 1 = opened)
    line_opening = model.addVars(CALENDAR, workcenters, vtype=gurobipy.GRB.BINARY, name="Open")
    # Variable total load (hours)
    total_hours = model.addVars(
        timeline, LINES, lb=0, ub=12, vtype=gurobipy.GRB.INTEGER, name="Total hours"
    )
    # Variable cost
    cost = model.addVars(timeline, workcenters, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="Cost")

    # CONSTRAINTS
    # Set the value of cost (hours * hourly cost)
    model.addConstrs(
        (
            (
                cost[(i, j)]
                == reg_hours[(i, j)] * wc_cost_reg[j] * line_opening[(i, j)]
                + ot_hours[(i, j)] * wc_cost_ot[j] * line_opening[(i, j)]
                for i in timeline
                for j in workcenters
            )
        ),
        name="Cost constr",
    )
    # Set the value of total load (regular + overtime)
    model.addConstrs(
        (
            (
                total_hours[(i, j)]
                == (reg_hours[(i, j)] + ot_hours[(i, j)]) * line_opening[(i, j)]
                for i in timeline
                for j in workcenters
            )
        ),
        name="Total hours constr",
    )

    # Constraint : requirement = load of the 3 lines
    model.addConstrs(
        ((total_hours.sum(d, "*") == needs[d] for d in timeline)),
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

    sol = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)
    sol = sol.filter(like="Total hours", axis=0)

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
CALENDAR = [
    "2020/7/15",
    "2020/7/16",
    "2020/7/17",
    "2020/7/18",
    "2020/7/19",
    "2020/7/20",
    "2020/7/21",
]

day_req = [30, 10, 34, 23, 23, 24, 25]
DAY_REQUIREMENTS = {d: day_req[i] for i, d in enumerate(CALENDAR)}
df_requirement = pd.DataFrame.from_dict({day: [day_req[i]] for i, day in enumerate(CALENDAR)})

# Weekdays / Weekends
weekdays = []
weekend = []
for i in CALENDAR:
    date = datetime.datetime.strptime(i, "%Y/%m/%d")
    if date.weekday() < 5:
        weekdays.append(i)
    else:
        weekend.append(i)

# Define the hourly cost per line - regular and overtime
LINES = ["Curtain_C1", "Curtain_C2", "Curtain_C3"]
regCost = [350, 300, 350]
REG_COST = {l: regCost[i] for i, l in enumerate(LINES)}
OTCost = [1.5 * i for i in regCost]
OT_COST = {l: OTCost[i] for i, l in enumerate(LINES)}

# Optimize the planning
solution = optimize_planning(CALENDAR, LINES, DAY_REQUIREMENTS, REG_COST, OT_COST)

# Format the result
optimized_planning = pd.DataFrame(index=LINES, columns=CALENDAR)
for line in LINES:
    for day in CALENDAR:
        optimized_planning.at[line, day] = solution.loc["Total hours[" + str(day) + "," + str(line) + "]"][0]

# Plot the new planning
plot_planning(optimized_planning, df_requirement)
