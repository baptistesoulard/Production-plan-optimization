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
from typing import List, Dict


def optimize_planning(
    timeline: List[str],
    workcenters: List[str],
    needs: Dict[str, int],
    wc_cost_reg: Dict[str, int],
    wc_cost_ot: Dict[str, int],
    wc_cost_we: Dict[str, int],
    inventory_cost: int,
) -> pd.DataFrame:

    # Weekdays / Weekends
    weekdays = []
    weekend = []
    for i in timeline:
        date = datetime.datetime.strptime(i, "%Y/%m/%d")
        if date.weekday() < 5:
            weekdays.append(i)
        else:
            weekend.append(i)

    # Initiate optimization model
    model = gurobipy.Model("Optimize production planning")

    # DEFINE VARIABLES
    # Load variables (hours) - regular and overtime
    reg_hours = model.addVars(
        timeline,
        workcenters,
        lb=7,
        ub=8,
        vtype=gurobipy.GRB.INTEGER,
        name="Regular hours",
    )
    ot_hours = model.addVars(
        timeline, workcenters, lb=0, ub=4, vtype=gurobipy.GRB.INTEGER, name="OT hours"
    )
    # Status of the line ( 0 = closed, 1 = opened)
    line_opening = model.addVars(
        timeline, workcenters, vtype=gurobipy.GRB.BINARY, name="Open"
    )
    # Variable total load (hours)
    total_hours = model.addVars(
        timeline,
        workcenters,
        lb=0,
        ub=12,
        vtype=gurobipy.GRB.INTEGER,
        name="Total hours",
    )
    # Variable cost
    cost = model.addVars(
        timeline, workcenters, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="Cost"
    )

    # Set the value of cost (hours * hourly cost)
    model.addConstrs(
        (
            (
                cost[(i, j)]
                == reg_hours[(i, j)] * wc_cost_reg[j] * line_opening[(i, j)]
                + ot_hours[(i, j)] * wc_cost_ot[j] * line_opening[(i, j)]
                for i in weekdays
                for j in workcenters
            )
        ),
        name="Cost weekdays",
    )
    model.addConstrs(
        (
            (
                cost[(i, j)]
                == (reg_hours[(i, j)] + ot_hours[(i, j)])
                * wc_cost_we[j]
                * line_opening[(i, j)]
                for i in weekend
                for j in workcenters
            )
        ),
        name="Cost weekend",
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
        name="Total hours = reg + OT",
    )

    # Constraint: requirement <= Load of the previous days
    print(needs)
    print(timeline)
    for k in range(len(timeline)):
        model.addConstr(
            (
                gurobipy.quicksum(
                    total_hours[(i, j)] for i in timeline[: k + 1] for j in workcenters
                )
            )
            >= (gurobipy.quicksum(needs[i] for i in timeline[: k + 1]))
        )

    # Constraint: Total hours of production = required production time
    model.addConstr(
        (
            gurobipy.quicksum(
                total_hours[(day, line)] for day in timeline for line in workcenters
            )
        )
        == (gurobipy.quicksum(needs[day] for day in timeline))
    )

    # Create variable "early production" and "inventory costs"
    early_prod = model.addVars(
        timeline, lb=0, vtype=gurobipy.GRB.INTEGER, name="early prod"
    )
    inventory_costs = model.addVars(
        timeline, lb=0, vtype=gurobipy.GRB.INTEGER, name="inventory costs"
    )

    # Set the value of gap for early production
    for k in range(len(timeline)):
        model.addConstr(
            (
                early_prod[timeline[k]]
                == (
                    gurobipy.quicksum(
                        total_hours[(i, j)] for j in lines for i in timeline[: k + 1]
                    )
                )
                - (gurobipy.quicksum(needs[i] for i in timeline[: k + 1]))
            )
        )

    # Set the value of inventory costs
    for k in range(len(timeline)):
        model.addConstr(
            (inventory_costs[timeline[k]] == early_prod[timeline[k]] * inventory_cost)
        )

        # DEFINE MODEL
    # Objective : minimize a function
    model.ModelSense = gurobipy.GRB.MINIMIZE
    # Function to minimize
    optimization_var = gurobipy.quicksum(
        cost[(i, j)] for i in timeline for j in workcenters
    ) + gurobipy.quicksum(inventory_costs[i] for i in timeline)

    objective = 0
    objective += optimization_var

    # SOLVE MODEL
    model.setObjective(objective)
    model.optimize()

    sol = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)
    sol = sol.filter(like="Total hours", axis=0)

    print("Total cost = $" + str(model.ObjVal))

    # FORMAT THE RESULT
    planning = sol
    planning["Date"] = list(planning.index.values)
    planning[["Date", "Line"]] = planning["Date"].str.split(",", expand=True)
    planning["Date"] = planning["Date"].str.split("[").str[1]
    planning["Line"] = planning["Line"].str.split("]").str[0]
    planning = planning.pivot(index="Line", columns="Date", values="Solution")

    return planning


def plot_planning(plan, need):
    plan = plan.T
    plan["Min capacity"] = 7
    plan["Max capacity"] = 12

    my_colors = ["skyblue", "salmon", "lightgreen"]

    fig, axs = plt.subplots(2)
    need.plot(
        kind="bar",
        width=0.2,
        title="Need in h per day",
        ax=axs[0],
        color="midnightblue",
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
    axs[1].get_legend().remove()

    plt.savefig("Result_Model3.png", bbox_inches="tight", dpi=1200)
    axe = plt.show()
    return axe


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
daily_requirements_df = pd.DataFrame.from_dict(daily_requirements, orient="index")

# Define the hourly cost per line - regular, overtime and weekend
reg_costs_per_line = {"Curtain_C1": 350, "Curtain_C2": 300, "Curtain_C3": 350}
ot_costs_per_line = {
    k: 1.5 * reg_costs_per_line[k] for k, v in reg_costs_per_line.items()
}
we_costs_per_line = {
    k: 2 * reg_costs_per_line[k] for k, w in reg_costs_per_line.items()
}

early_prod_cost = 17

lines: List[str] = list(reg_costs_per_line.keys())

# Optimize the planning
solution = optimize_planning(
    calendar,
    lines,
    daily_requirements,
    reg_costs_per_line,
    ot_costs_per_line,
    we_costs_per_line,
    early_prod_cost,
)

# Plot the new planning
plot_planning(solution, daily_requirements_df)
