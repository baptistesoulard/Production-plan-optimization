# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:09:01 2020
@author: Baptiste Soulard
"""

# Import required packages
import pandas as pd
import gurobipy
from typing import List, Dict
import altair as alt
import altair_saver


def optimize_planning(
    timeline: List[str],
    workcenters: List[str],
    needs: Dict[str, int],
    wc_cost_reg: Dict[str, int],
) -> pd.DataFrame:

    # Initiate optimization model
    model = gurobipy.Model("Optimize production planning")

    # DEFINE VARIABLES
    # Variable total load (hours)
    working_hours = model.addVars(
        timeline,
        workcenters,
        lb=7,
        ub=12,
        vtype=gurobipy.GRB.INTEGER,
        name="Working hours",
    )

    # Status of the line ( 0 = closed, 1 = opened)
    line_opening = model.addVars(
        timeline, workcenters, vtype=gurobipy.GRB.BINARY, name="Open status"
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
    labor_cost = model.addVars(
        timeline, workcenters, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="Labor cost"
    )

    # CONSTRAINTS
    # Set the value of total load
    model.addConstrs(
        (
            total_hours[(date, wc)]
            == working_hours[(date, wc)] * line_opening[(date, wc)]
            for date in timeline
            for wc in workcenters
        ),
        name="Link total hours - reg/ot hours",
    )

    # Set the value of cost (hours * hourly cost)
    model.addConstrs(
        (
            labor_cost[(date, wc)]
            == total_hours[(date, wc)] * wc_cost_reg[wc] * line_opening[(date, wc)]
            for date in timeline
            for wc in workcenters
        ),
        name="Link labor cost - working hours",
    )

    # Total load = requirement
    model.addConstrs(
        ((total_hours.sum(date, "*") == needs[date] for date in timeline)),
        name="Link total hours - requirement",
    )

    # DEFINE MODEL
    # Objective : minimize a function
    model.ModelSense = gurobipy.GRB.MINIMIZE
    # Function to minimize
    optimization_var = gurobipy.quicksum(
        labor_cost[(date, wc)] for date in timeline for wc in workcenters
    )
    objective = 0
    objective += optimization_var

    # SOLVE MODEL
    model.setObjective(objective)
    model.optimize()

    sol = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)

    print("Total cost = $" + str(model.ObjVal))
    return sol


def plot_planning(planning, need, timeline):
    # Plot graph - Requirement
    source = need.copy()
    source = source.rename(columns={0: "Hours"})
    source["Date"] = source.index

    bars_need = (alt.Chart(source).mark_bar().encode(y="Hours:Q")).properties(
        width=600 / len(timeline) - 22, height=120
    )

    text_need = bars_need.mark_text(
        align="left", baseline="middle", dx=-8, dy=-7
    ).encode(text="Hours:Q")

    chart_need = (
        alt.layer(bars_need, text_need, data=source)
        .facet(column="Date:N")
        .properties(title="Requirement")
    )

    # Plot graph - Optimized planning
    source = planning.filter(like="Total hours", axis=0).copy()
    source["Date"] = list(source.index.values)
    source = source.rename(columns={"Solution": "Hours"}).reset_index()
    source[["Date", "Line"]] = source["Date"].str.split(",", expand=True)
    source["Date"] = source["Date"].str.split("[").str[1]
    source["Line"] = source["Line"].str.split("]").str[0]
    source["Min capacity"] = 7
    source["Max capacity"] = 12
    source = source.round({"Hours": 1})

    bars = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            x="Line:N",
            y="Hours:Q",
            color="Line:N",
        )
        .properties(width=600 / len(timeline) - 22)
    )

    text = bars.mark_text(align="left", baseline="middle", dx=-8, dy=-7).encode(
        text="Hours:Q"
    )

    line_min = alt.Chart(source).mark_rule(color="darkgrey").encode(y="Min capacity:Q")

    line_max = alt.Chart(source).mark_rule(color="darkgrey").encode(y="Max capacity:Q")

    chart_planning = (
        alt.layer(bars, text, line_min, line_max, data=source)
        .facet(column="Date:N")
        .properties(title="Optimized Production Planning")
    )

    chart = alt.vconcat(chart_planning, chart_need)
    chart.save("planning_time_model1.html")


# Define daily requirement
daily_requirements: Dict[str, int] = {
    "2020/7/13": 30,
    "2020/7/14": 10,
    "2020/7/15": 34,
    "2020/7/16": 25,
    "2020/7/17": 23,
    "2020/7/18": 24,
    "2020/7/19": 25,
}

calendar: List[str] = list(daily_requirements.keys())
daily_requirements_df = pd.DataFrame.from_dict(daily_requirements, orient="index")

# Define hourly cost per line - regular, overtime and weekend
reg_costs_per_line = {"Line_1": 245, "Line_2": 315, "Line_3": 245}

lines: List[str] = list(reg_costs_per_line.keys())

# Optimize planning
solution = optimize_planning(
    calendar,
    lines,
    daily_requirements,
    reg_costs_per_line,
)

# Plot the new planning
plot_planning(solution, daily_requirements_df, calendar)
