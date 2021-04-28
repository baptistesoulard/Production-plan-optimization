# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:09:01 2020
@author: Baptiste Soulard
"""

# Import required packages
import pandas as pd
import gurobipy
import datetime
from typing import List, Dict
import altair as alt


def optimize_planning(
    timeline: List[str],
    workcenters: List[str],
    needs: Dict[str, int],
    wc_cost_reg: Dict[str, int],
    wc_cost_ot: Dict[str, int],
    wc_cost_we: Dict[str, int],
) -> pd.DataFrame:

    # Split weekdays/weekends
    weekdays = []
    weekend = []
    for date in timeline:
        day = datetime.datetime.strptime(date, "%Y/%m/%d")
        if day.weekday() < 5:
            weekdays.append(date)
        else:
            weekend.append(date)

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
        timeline,
        workcenters,
        lb=0,
        ub=4,
        vtype=gurobipy.GRB.INTEGER,
        name="Overtime hours",
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
    # Set the value of total load (regular + overtime)
    model.addConstrs(
        (
            total_hours[(date, wc)]
            == (reg_hours[(date, wc)] + ot_hours[(date, wc)]) * line_opening[(date, wc)]
            for date in timeline
            for wc in workcenters
        ),
        name="Link total hours - reg/ot hours",
    )

    # Set the value of cost (hours * hourly cost)
    model.addConstrs(
        (
            labor_cost[(date, wc)]
            == reg_hours[(date, wc)] * wc_cost_reg[wc] * line_opening[(date, wc)]
            + ot_hours[(date, wc)] * wc_cost_ot[wc] * line_opening[(date, wc)]
            for date in weekdays
            for wc in workcenters
        ),
        name="Link labor cost - working hours - wd",
    )

    model.addConstrs(
        (
            labor_cost[(date, wc)] == total_hours[(date, wc)] * wc_cost_we[wc]
            for date in weekend
            for wc in workcenters
        ),
        name="Link labor cost - working hours - we",
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
    objective = 0
    objective += gurobipy.quicksum(
        labor_cost[(date, wc)] for date in timeline for wc in workcenters
    )

    # SOLVE MODEL
    model.setObjective(objective)
    model.optimize()

    sol = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)

    print("Total cost = $" + str(model.ObjVal))
    return sol


def plot_planning(
    planning: pd.DataFrame, need: pd.DataFrame, timeline: pd.DataFrame
) -> None:
    # Plot graph - Requirement
    source = need.copy()
    source = source.rename(columns={0: "Hours"})
    source["Date"] = source.index

    bars_need = (alt.Chart(source).mark_bar().encode(y="Hours:Q")).properties(
        width=600 / len(timeline) - 22, height=90
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
    source["Load%"] = pd.Series(
        ["{0:.0f}%".format(val / 8 * 100) for val in source["Hours"]],
        index=source.index,
    )

    bars = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            x="Line:N",
            y="Hours:Q",
            color="Line:N",
            tooltip=["Date", "Line", "Hours", "Load%"],
        )
        .interactive()
        .properties(width=600 / len(timeline) - 22, height=200)
    )

    line_min = alt.Chart(source).mark_rule(color="darkgrey").encode(y="Min capacity:Q")

    line_max = (
        alt.Chart(source)
            .mark_rule(color="darkgrey")
            .encode(y=alt.Y("Max capacity:Q", title="Load (hours)"))
    )

    chart = (
        alt.layer(bars, line_min, line_max, data=source)
            .facet(column="Date:N")
            .properties(title="Daily working time", background='#00000000')
    )

    chart.save("planning_time_model2.html")


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
ot_costs_per_line = {
    k: 1.5 * reg_costs_per_line[k] for k, v in reg_costs_per_line.items()
}
we_costs_per_line = {
    k: 2 * reg_costs_per_line[k] for k, w in reg_costs_per_line.items()
}

lines: List[str] = list(reg_costs_per_line.keys())

# Optimize planning
solution = optimize_planning(
    calendar,
    lines,
    daily_requirements,
    reg_costs_per_line,
    ot_costs_per_line,
    we_costs_per_line,
)

# Plot the new planning
plot_planning(solution, daily_requirements_df, calendar)
