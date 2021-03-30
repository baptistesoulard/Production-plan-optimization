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
    x_qty = model.addVars(
        timeline,
        manufacturing_orders,
        workcenters,
        lb=0,
        vtype=gurobipy.GRB.INTEGER,
        name="plannedQty",
    )
    x_time = model.addVars(
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
                x_time[(date, mo, wc)]
                == x_qty[(date, mo, wc)] * cycle_times[(mo, wc)]
                for date in timeline
                for mo in manufacturing_orders
                for wc in workcenters
            )
        ),
        name="x_time_constr",
    )

    # Qty to display
    quantity = model.addVars(
        timeline, workcenters, lb=0, vtype=gurobipy.GRB.INTEGER, name="qty"
    )

    # Set the value of qty
    model.addConstrs(
        (
            (
                quantity[(date, wc)]
                == gurobipy.quicksum(
                    x_qty[(date, mo, wc)] for mo in manufacturing_orders
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
                    x_time[(date, mo, wc)] for mo in manufacturing_orders
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
            gurobipy.quicksum(
                x_qty[(date, mo, wc)]
                for date in timeline
                for mo in manufacturing_orders
                for wc in workcenters
            )
            == gurobipy.quicksum(
                needs[(date, mo)] for date in timeline for mo in manufacturing_orders
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
    for day in range(len(timeline)):
        model.addConstrs(
            (
                gap_prod[(timeline[day], mo)]
                == gurobipy.quicksum(
                    x_qty[(date, mo, wc)]
                    for date in timeline[: day + 1]
                    for wc in workcenters
                )
                - gurobipy.quicksum(needs[(date, mo)] for date in timeline[: day + 1])
                for mo in manufacturing_orders
            ),
            name="gap_prod",
        )

    # Set the value of ABS(gap for early production)
    model.addConstrs(
        (
            (abs_gap_prod[(date, mo)] == gurobipy.abs_(gap_prod[(date, mo)]))
            for date in timeline
            for mo in manufacturing_orders
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
            (
                early_prod[(date, mo)]
                == (gap_prod[(date, mo)] + abs_gap_prod[(date, mo)]) / 2
            )
            for date in timeline
            for mo in manufacturing_orders
        ),
        name="early_prod",
    )

    # Gap late production
    late_prod = model.addVars(
        timeline, manufacturing_orders, vtype=gurobipy.GRB.CONTINUOUS, name="lateProd"
    )

    # Set the value of gap for late production
    model.addConstrs(
        (
            (
                late_prod[(date, mo)]
                == (gap_prod[(date, mo)] - abs_gap_prod[(date, mo)]) / 2
            )
            for date in timeline
            for mo in manufacturing_orders
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


def plot_load(planning: pd.DataFrame, need: pd.DataFrame, timeline: List[str]) -> None:

    # Plot graph - Requirement
    source = pd.Series(need).rename_axis(["Date", "MO_No"]).reset_index(name="Qty")
    source = source.groupby(["Date"]).sum()
    source["Date"] = source.index

    chart_need = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            y=alt.Y("Qty", axis=alt.Axis(grid=False)),
            column=alt.Column("Date:N"),
            tooltip=["Qty"],
        )
        .interactive()
        .properties(
            width=600 / len(calendar) - 22,
            height=90,
            title="Requirement",
        )
    )

    # Plot graph - Optimized planning
    source = planning.filter(like="Total hours", axis=0).copy()
    source["Date"] = source.index
    source = source.reset_index(drop=True)
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
        .encode(y=alt.Y("Max capacity:Q", title="Load"))
    )

    chart_planning = (
        alt.layer(bars, line_min, line_max, data=source)
        .facet(column="Date:N")
        .properties(title="Optimized Production Planning")
    )

    chart = alt.vconcat(chart_planning, chart_need)
    chart.save("planning_load_model4.html")


def plot_planning(planning: pd.DataFrame, need: pd.DataFrame, timeline: List[str]) -> None:

    # Plot graph - Requirement
    source = pd.Series(need).rename_axis(["Date", "MO_No"]).reset_index(name="Qty")

    chart_need = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            y=alt.Y("Qty", axis=alt.Axis(grid=False)),
            column=alt.Column("Date:N"),
            color="MO_No:N",
            tooltip=["MO_No", "Qty"],
        )
        .interactive()
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
            tooltip=["Line", "MO_No", "Qty"],
        )
        .interactive()
        .properties(
            width=600 / len(timeline) - 22,
            height=200,
            title="Optimized Curtain Planning",
        )
    )

    chart = alt.vconcat(chart_planning, chart_need)
    chart.save("planning_MO_model4.html")


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

# Get cycle times
capacity = pd.read_excel("Constraints.xlsx", sheet_name="9.5h capacity").set_index(
    "Line"
)
cycle_time = capacity.rdiv(9.5)

# Get MO List
manufacturing_orders = pd.read_excel("Requirement.xlsx")
MO_list = manufacturing_orders["MO_No"].to_list()


def check_duplicates(list_to_check):
    if len(list_to_check) == len(set(list_to_check)):
        return
    else:
        print("Duplicate MO, please check the requirements file")
        exit()
        return


check_duplicates(MO_list)

# Combine MO and cycle times
manufacturing_orders = manufacturing_orders.merge(
    cycle_time, left_on="MPS_Family", right_index=True
)
manufacturing_orders = manufacturing_orders.rename(
    columns={"Line_1": "CT_1", "Line_2": "CT_2", "Line_3": "CT_3"}
)
manufacturing_orders["Planned_Finish_Date"] = pd.to_datetime(
    manufacturing_orders["Planned_Finish_Date"]
).dt.strftime("%Y/%m/%d")
manufacturing_orders = manufacturing_orders.sort_values(
    by=["Planned_Finish_Date", "MO_No"]
)

CT_df = manufacturing_orders[["MO_No", "CT_1", "CT_2", "CT_3"]]
CT_df = CT_df.set_index("MO_No")
CT_dict = {
    (m, l): CT_df.iloc[j][k] for j, m in enumerate(MO_list) for k, l in enumerate(lines)
}

# Define calendar
start_date = datetime.datetime.strptime(
    manufacturing_orders["Planned_Finish_Date"].min(), "%Y/%m/%d"
)
end_date = datetime.datetime.strptime(
    manufacturing_orders["Planned_Finish_Date"].max(), "%Y/%m/%d"
)

date_modified = start_date
calendar = [start_date.strftime("%Y/%m/%d")]

while date_modified < end_date:
    date_modified += datetime.timedelta(days=1)
    calendar.append(date_modified.strftime("%Y/%m/%d"))

# Define daily requirement dataframe
manufacturing_orders = manufacturing_orders[["MO_No", "Qty", "Planned_Finish_Date"]]
manufacturing_orders = manufacturing_orders.append(
    pd.DataFrame(
        {
            "MO_No": ["temp" for _ in range(len(calendar))],
            "Planned_Finish_Date": calendar,
        }
    )
)
manufacturing_orders = manufacturing_orders.pivot(
    index="MO_No", columns="Planned_Finish_Date", values="Qty"
)
manufacturing_orders = manufacturing_orders.drop("temp", axis=0).fillna(0)

daily_requirements = {
    (i, j): manufacturing_orders[i][j] for i in calendar for j in MO_list
}
daily_requirements_df = pd.DataFrame.from_dict(daily_requirements, orient="index")

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
plot_load(solution, daily_requirements, calendar)
print_planning(solution)
plot_planning(solution, daily_requirements, calendar)
