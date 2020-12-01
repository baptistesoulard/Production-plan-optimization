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
    needs,
    wc_cost_reg: Dict[str, int],
    wc_cost_ot: Dict[str, int],
    wc_cost_we: Dict[str, int],
    inventory_carrying_cost: int,
    manufacturing_orders: List[str],
    cycle_times,
    delay_cost: int,
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
    # Quantity and time variables
    x_qty_var = model.addVars(
        timeline,
        manufacturing_orders,
        workcenters,
        lb=0,
        vtype=gurobipy.GRB.INTEGER,
        name="plannedQty",
    )
    x_time_var = model.addVars(
        timeline,
        manufacturing_orders,
        workcenters,
        lb=0,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="plannedTime",
    )

    # Set the value of x_time
    model.addConstrs(
        (
            (
                x_time_var[(date, mo, wc)]
                == x_qty_var[(date, mo, wc)] * cycle_times[(mo, wc)]
                for date in timeline
                for mo in manufacturing_orders
                for wc in workcenters
            )
        ),
        name="x_time_constr",
    )

    # Qty to display
    qty_var = model.addVars(
        timeline, workcenters, lb=0, vtype=gurobipy.GRB.INTEGER, name="qty"
    )

    # Set the value of qty
    model.addConstrs(
        (
            (
                qty_var[(date, wc)]
                == gurobipy.quicksum(
                    x_qty_var[(date, mo, wc)] for mo in manufacturing_orders
                )
                for date in timeline
                for wc in workcenters
            )
        ),
        name="wty_time_constr",
    )

    # Load variables (hours) - regular and overtime
    reg_hours = model.addVars(
        timeline,
        workcenters,
        lb=7,
        ub=8,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="Regular hours",
    )
    ot_hours = model.addVars(
        timeline,
        workcenters,
        lb=0,
        ub=4,
        vtype=gurobipy.GRB.CONTINUOUS,
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
        vtype=gurobipy.GRB.CONTINUOUS,
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

    # Constraint: Total hours of production = required production time
    model.addConstrs(
        (
            (
                total_hours[(date, wc)]
                == gurobipy.quicksum(
                    x_time_var[(date, mo, wc)] for mo in manufacturing_orders
                )
                for date in timeline
                for wc in workcenters
            )
        ),
        name="total_hours_constr",
    )

    # Constraint: Total hours of production = required production time
    model.addConstr(
        (
            (
                gurobipy.quicksum(
                    x_qty_var[(i, j, k)]
                    for i in timeline
                    for j in manufacturing_orders
                    for k in workcenters
                )
                == (
                    gurobipy.quicksum(
                        needs[(i, j)] for i in timeline for j in manufacturing_orders
                    )
                )
            )
        ),
        name="total_req",
    )

    # Gap early/late production
    gap_prod = model.addVars(
        timeline, manufacturing_orders, vtype=gurobipy.GRB.CONTINUOUS, name="gapProd"
    )
    abs_gap_prod = model.addVars(
        timeline, manufacturing_orders, vtype=gurobipy.GRB.CONTINUOUS, name="absGapProd"
    )

    # Set the value of gap for early production
    for l in range(len(timeline)):
        model.addConstrs(
            (
                (
                    gap_prod[(timeline[l], j)]
                    == (
                        gurobipy.quicksum(
                            x_qty_var[(i, j, k)]
                            for i in timeline[: l + 1]
                            for k in workcenters
                        )
                    )
                    - (gurobipy.quicksum(needs[(i, j)] for i in timeline[: l + 1]))
                    for j in manufacturing_orders
                )
            ),
            name="gap_prod",
        )

    # Set the value of ABS(gap for early production)
    model.addConstrs(
        (
            (abs_gap_prod[(i, j)] == gurobipy.abs_(gap_prod[(i, j)]))
            for i in timeline
            for j in manufacturing_orders
        ),
        name="abs_gap_prod",
    )

    # Definition gap early production
    early_prod = model.addVars(
        timeline, manufacturing_orders, vtype=gurobipy.GRB.CONTINUOUS, name="earlyProd"
    )

    # Set the value of gap for early production
    model.addConstrs(
        (
            (early_prod[(i, j)] == (gap_prod[(i, j)] + abs_gap_prod[(i, j)]) / 2)
            for i in timeline
            for j in manufacturing_orders
        ),
        name="early_prod",
    )

    # Gap late production
    late_prod = model.addVars(
        timeline, manufacturing_orders, vtype=gurobipy.GRB.CONTINUOUS, name="lateProd"
    )

    # Set the value of gap for lateproduction
    model.addConstrs(
        (
            (late_prod[(i, j)] == (gap_prod[(i, j)] - abs_gap_prod[(i, j)]) / 2)
            for i in timeline
            for j in manufacturing_orders
        ),
        name="late_prod",
    )

    # DEFINE MODEL
    # Objective : minimize a function
    model.ModelSense = gurobipy.GRB.MINIMIZE
    # Function to minimize
    objective = 0
    objective += gurobipy.quicksum(
        labor_cost[(date, wc)] for date in timeline for wc in workcenters
    )
    objective += gurobipy.quicksum(
        early_prod[(date, mo)] * inventory_carrying_cost
        for date in timeline
        for mo in manufacturing_orders
    )
    objective += gurobipy.quicksum(
        late_prod[(date, mo)] * delay_cost
        for date in timeline
        for mo in manufacturing_orders
    )

    # SOLVE MODEL
    model.setObjective(objective)
    model.optimize()

    sol = pd.DataFrame(data={"Solution": model.X}, index=model.VarName)

    print("Total cost = $" + str(model.ObjVal))

    # model.write("Planning_optimization.lp")
    # file = open("Planning_optimization.lp", 'r')
    # print(file.read())
    # file.close()

    return sol


def plot_load(planning: pd.DataFrame, timeline: pd.DataFrame) -> None:

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
        .properties(width=600 / len(timeline) - 22, height=200)
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

    chart_planning.save("planning_load_model4.html")


def print_planning(planning: pd.DataFrame) -> None:

    df = (
        planning.filter(like="plannedQty", axis=0)
        .copy()
        .rename(columns={"Solution": "Qty"})
        .reset_index()
    )
    df[["Date", "MO_No", "Line"]] = df["index"].str.split(",", expand=True)
    df["Date"] = df["Date"].str.split("[").str[1]
    df["Line"] = df["Line"].str.split("]").str[0]
    df = df[["Date", "Line", "Qty", "MO_No"]]

    df.to_csv(r"Planning_model4_list.csv", index=True)
    df.pivot_table(values="Qty", index="MO_No", columns=["Date", "Line"]).to_csv(
        r"Planning_model4v2.csv", index=True
    )


def plot_planning(planning: pd.DataFrame, need, timeline: pd.DataFrame) -> None:

    # Plot graph - Requirement
    source = pd.Series(need).rename_axis(["Date", "MO_No"]).reset_index(name="Qty")

    chart_need = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            y=alt.Y("Qty", axis=alt.Axis(grid=False)),
            column=alt.Column("Date:N"),
            color="MO_No:N",
        )
        .properties(
            width=600 / len(timeline) - 22,
            height=90,
            title="test",
        )
    )

    df = (
        planning.filter(like="plannedQty", axis=0)
        .copy()
        .rename(columns={"Solution": "Qty"})
        .reset_index()
    )
    df[["Date", "MO_No", "Line"]] = df["index"].str.split(",", expand=True)
    df["Date"] = df["Date"].str.split("[").str[1]
    df["Line"] = df["Line"].str.split("]").str[0]
    df = df[["Date", "Line", "Qty", "MO_No"]]

    chart_planning = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y("Qty", axis=alt.Axis(grid=False)),
            x="Line:N",
            column=alt.Column("Date:N"),
            color="MO_No:N",
        )
        .properties(
            width=600 / len(timeline) - 22,
            height=200,
            title="Optimized Curtain Planning",
        )
    )

    chart = alt.vconcat(chart_planning, chart_need)
    chart.save("planning_time_model4.html")


# Define daily requirement
# Calendar
days_list = [
    "2020/07/13",
    "2020/07/14",
    "2020/07/15",
    "2020/07/16",
    "2020/07/17",
    "2020/07/18",
    "2020/07/19",
]

# Get MO List
MO_file = "Requirement.xlsx"
MO_df = pd.read_excel(MO_file)
MO_list = MO_df["MO_No"].to_list()

# Get cycle times
constraints_file = "Constraints.xlsx"
capacity_df = pd.read_excel(constraints_file, sheet_name="9.5h capacity").set_index(
    "Line"
)
cycleTime_df = capacity_df.rdiv(9.5)

# Combine MO and cycle times
MO_df = MO_df.merge(cycleTime_df, left_on="MPS_Family", right_index=True)

MO_df = MO_df.rename(columns={"Line_1": "CT_1", "Line_2": "CT_2", "Line_3": "CT_3"})

MO_df["Planned_Finish_Date"] = pd.to_datetime(MO_df["Planned_Finish_Date"]).dt.strftime(
    "%Y/%m/%d"
)
MO_df = MO_df.sort_values(by=["Planned_Finish_Date", "MO_No"])

dayReq_df = MO_df[["MO_No", "Qty", "Planned_Finish_Date"]]

temp = ["temp" for _ in range(len(days_list))]
xtra = {"MO_No": temp, "Planned_Finish_Date": days_list}

dayReq_df = dayReq_df.append(pd.DataFrame(xtra))

dayReq_df = dayReq_df.pivot(index="MO_No", columns="Planned_Finish_Date", values="Qty")
dayReq_df = dayReq_df.drop("temp", axis=0).fillna(0)

daily_requirements = {(i, j): dayReq_df[i][j] for i in days_list for j in MO_list}

calendar = [
    "2020/07/13",
    "2020/07/14",
    "2020/07/15",
    "2020/07/16",
    "2020/07/17",
    "2020/07/18",
    "2020/07/19",
]
daily_requirements_df = pd.DataFrame.from_dict(daily_requirements, orient="index")

# Define hourly cost per line - regular, overtime and weekend
reg_costs_per_line = {"Line_1": 245, "Line_2": 315, "Line_3": 245}
ot_costs_per_line = {
    k: 1.5 * reg_costs_per_line[k] for k, v in reg_costs_per_line.items()
}
we_costs_per_line = {
    k: 2 * reg_costs_per_line[k] for k, w in reg_costs_per_line.items()
}

storage_cost = 5
late_prod_cost = 1000

lines: List[str] = list(reg_costs_per_line.keys())

CT_df = MO_df[["MO_No", "CT_1", "CT_2", "CT_3"]]
CT_df = CT_df.set_index("MO_No")
CT_dict = {
    (m, l): CT_df.iloc[j][k] for j, m in enumerate(MO_list) for k, l in enumerate(lines)
}

# Optimize planning
solution = optimize_planning(
    calendar,
    lines,
    daily_requirements,
    reg_costs_per_line,
    ot_costs_per_line,
    we_costs_per_line,
    storage_cost,
    MO_list,
    CT_dict,
    late_prod_cost,
)

# Plot the new planning
plot_load(solution, calendar)
print_planning(solution)
plot_planning(solution, daily_requirements, calendar)