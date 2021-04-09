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
import datapane as dp


def optimize_planning(
        timeline: List[str],
        workcenters: List[str],
        needs,
        wc_cost_reg: Dict[str, int],
        wc_cost_ot: Dict[str, int],
        wc_cost_we: Dict[str, int],
        inventory_carrying_cost: int,
        customer_orders: List[str],
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
    # Quantity variable
    x_qty = model.addVars(
        timeline,
        customer_orders,
        workcenters,
        lb=0,
        vtype=gurobipy.GRB.INTEGER,
        name="plannedQty",
    )

    # Time variable
    x_time = model.addVars(
        timeline,
        customer_orders,
        workcenters,
        lb=0,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="plannedTime",
    )

    # Set the value of x_time
    model.addConstrs(
        (
            (
                x_time[(date, mo, wc)] == x_qty[(date, mo, wc)] * cycle_times[(mo, wc)]
                for date in timeline
                for mo in customer_orders
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
                == gurobipy.quicksum(x_qty[(date, mo, wc)] for mo in customer_orders)
                for date in timeline
                for wc in workcenters
            )
        ),
        name="wty_time_constr",
    )

    # Variable status of the line ( 0 = closed, 1 = opened)
    line_opening = model.addVars(
        timeline, workcenters, vtype=gurobipy.GRB.BINARY, name="Open status"
    )

    # Load variables (hours) - regular and overtime
    reg_hours = model.addVars(
        timeline,
        workcenters,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="Regular hours",
    )

    ot_hours = model.addVars(
        timeline,
        workcenters,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="Overtime hours",
    )

    reg_hours_bis = model.addVars(
        timeline,
        workcenters,
        lb=7,
        ub=8,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="regHours",
    )
    ot_hours_bis = model.addVars(
        timeline, workcenters, lb=0, ub=4, vtype=gurobipy.GRB.CONTINUOUS, name="OTHours"
    )

    # Set the value of reg and OT hours)
    model.addConstrs(
        (
            reg_hours[(date, wc)]
            == reg_hours_bis[(date, wc)] * line_opening[(date, wc)]
            for date in timeline
            for wc in workcenters
        ),
        name="total_hours_constr",
    )

    model.addConstrs(
        (
            ot_hours[(date, wc)] == ot_hours_bis[(date, wc)] * line_opening[(date, wc)]
            for date in timeline
            for wc in workcenters
        ),
        name="total_hours_constr",
    )

    # Variable total load (hours)
    total_hours = model.addVars(
        timeline,
        workcenters,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="Total hours",
    )

    # Set the value of total load (regular + overtime)
    model.addConstrs(
        (
            total_hours[(date, wc)] == (reg_hours[(date, wc)] + ot_hours[(date, wc)])
            for date in timeline
            for wc in workcenters
        ),
        name="Link total hours - reg/ot hours",
    )

    # Set total hours of production in link with the time variable
    model.addConstrs(
        (
            (
                total_hours[(date, wc)]
                == gurobipy.quicksum(x_time[(date, mo, wc)] for mo in customer_orders)
                for date in timeline
                for wc in workcenters
            )
        ),
        name="total_hours_constr",
    )

    # Variable cost
    labor_cost = model.addVars(
        timeline, workcenters, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name="Labor cost"
    )

    # Set the value of cost (hours * hourly cost)
    model.addConstrs(
        (
            labor_cost[(date, wc)]
            == reg_hours[(date, wc)] * wc_cost_reg[wc]
            + ot_hours[(date, wc)] * wc_cost_ot[wc]
            for date in weekdays
            for wc in workcenters
        ),
        name="Link labor cost - working hours - wd",
    )

    model.addConstrs(
        (
            labor_cost[(date, wc)]
            == total_hours[(date, wc)] * wc_cost_we[wc]
            for date in weekend
            for wc in workcenters
        ),
        name="Link labor cost - working hours - we",
    )

    # Variable gap early/late production
    gap_prod = model.addVars(
        timeline,
        customer_orders,
        lb=-10000,
        ub=10000,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="gapProd",
    )
    abs_gap_prod = model.addVars(
        timeline,
        customer_orders,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="absGapProd",
    )
    # Set the value of gap for early production
    for l in range(len(timeline)):
        model.addConstrs(
            (
                gap_prod[(timeline[l], mo)]
                == gurobipy.quicksum(
                    x_qty[(date, mo, wc)]
                    for date in timeline[: l + 1]
                    for wc in workcenters
                )
                - (gurobipy.quicksum(needs[(date, mo)] for date in timeline[: l + 1]))
                for mo in customer_orders
            ),
            name="gap_prod",
        )

    # Set the value of ABS(gap for early production)
    model.addConstrs(
        (
            (abs_gap_prod[(date, mo)] == gurobipy.abs_(gap_prod[(date, mo)]))
            for date in timeline
            for mo in customer_orders
        ),
        name="abs gap prod",
    )

    # Create variable "early production" and "inventory costs"
    early_prod = model.addVars(
        timeline,
        customer_orders,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="early prod",
    )
    inventory_costs = model.addVars(
        timeline,
        customer_orders,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="inventory costs",
    )

    # Set the value of early production
    model.addConstrs(
        (
            early_prod[(date, m)] == (gap_prod[(date, m)] + abs_gap_prod[(date, m)]) / 2
            for date in timeline
            for m in customer_orders
        ),
        name="early prod",
    )

    # Set the value of inventory costs
    model.addConstrs(
        (
            (inventory_costs[(date, m)] == early_prod[(date, m)] * inventory_carrying_cost)
            for date in timeline
            for m in customer_orders
        ),
        name="inventory costs",
    )

    # Create variable "late production" and "delay costs"
    late_prod = model.addVars(
        timeline,
        customer_orders,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="late prod",
    )
    delay_costs = model.addVars(
        timeline,
        customer_orders,
        vtype=gurobipy.GRB.CONTINUOUS,
        name="inventory costs",
    )

    # Set the value of late production
    model.addConstrs(
        (
            late_prod[(date, m)] == (abs_gap_prod[(date, m)] - gap_prod[(date, m)]) / 2
            for date in timeline
            for m in customer_orders
        ),
        name="late prod",
    )

    # Set the value of delay costs
    model.addConstrs(
        (
            (delay_costs[(date, m)] == late_prod[(date, m)] * delay_cost)
            for date in timeline
            for m in customer_orders
        ),
        name="delay costs",
    )

    # CONSTRAINT
    # Constraint: Total hours of production = required production time
    model.addConstr(
        (
            gurobipy.quicksum(
                x_qty[(date, mo, wc)]
                for date in timeline
                for mo in customer_orders
                for wc in workcenters
            )
            == (gurobipy.quicksum(needs[(date, mo)] for date in timeline for mo in customer_orders))
        ),
        name="total_req",
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
        inventory_costs[(date, mo)]
        for date in timeline
        for mo in customer_orders
    )
    objective += gurobipy.quicksum(
        delay_costs[(date, mo)]
        for date in timeline
        for mo in customer_orders
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
    source = (
        pd.Series(need).rename_axis(["Date", "Customer_Order"]).reset_index(name="Qty")
    )
    source = source.groupby(["Date"]).sum()
    source["Date"] = source.index

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
            .properties(width=550 / len(timeline) - 22, height=150)
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
            .properties(title="Daily working time")
    )

    # chart = alt.vconcat(chart_planning, chart_need)
    chart.save("planning_load_model4.html")

    dp.Report(
        '### Working time',
        dp.Plot(chart, caption="Production schedule model 4 - Time")
    ).publish(name='Optimized production schedule - Time',
              description="Optimized production schedule - Time", open=True)


def plot_planning(
        planning: pd.DataFrame, need: pd.DataFrame, timeline: List[str]
) -> None:
    # Plot graph - Requirement
    source = pd.Series(need).rename_axis(["Date", "Order"]).reset_index(name="Qty")

    chart_need = (
        alt.Chart(source)
            .mark_bar()
            .encode(
            y=alt.Y("Qty", axis=alt.Axis(grid=False)),
            column=alt.Column("Date:N"),
            color="Order:N",
            tooltip=["Order", "Qty"],
        )
            .interactive()
            .properties(
            width=800 / len(timeline) - 22,
            height=100,
            title="Customer's requirement",
        )
    )

    df = (
        planning.filter(like="plannedQty", axis=0)
            .copy()
            .rename(columns={"Solution": "Qty"})
            .reset_index()
    )
    df[["Date", "Order", "Line"]] = df["index"].str.split(",", expand=True)
    df["Date"] = df["Date"].str.split("[").str[1]
    df["Line"] = df["Line"].str.split("]").str[0]
    df = df[["Date", "Line", "Qty", "Order"]]

    chart_planning = (
        alt.Chart(df)
            .mark_bar()
            .encode(
            y=alt.Y("Qty", axis=alt.Axis(grid=False)),
            x="Line:N",
            column=alt.Column("Date:N"),
            color="Order:N",
            tooltip=["Line", "Order", "Qty"],
        )
            .interactive()
            .properties(
            width=800 / len(timeline) - 22,
            height=200,
            title="Optimized Production Schedule",
        )
    )

    chart = alt.vconcat(chart_planning, chart_need)
    chart.save("planning_MO_model4.html")

    dp.Report(
        '### Production schedule',
        dp.Plot(chart, caption="Production schedule model 4 - Qty")
    ).publish(name='Optimized production schedule - Qty2',
              description="Optimized production schedule - Qty", open=True)


def plot_inventory(
        planning: pd.DataFrame, timeline: List[str], cust_orders,
) -> None:
    # Plot inventory
    df = (
        planning.filter(like="early prod", axis=0)
            .copy()
            .rename(columns={"Solution": "Qty"})
            .reset_index()
    )

    df[["Date", "Order"]] = df["index"].str.split(",", expand=True)
    df["Date"] = df["Date"].str.split("[").str[1]
    df["Order"] = df["Order"].str.split("]").str[0]
    df = df[["Date", "Qty", "Order"]]

    models_list = cust_orders[['Order', 'Product_Family']]
    df = pd.merge(df, models_list, on='Order', how='inner')
    df = df[["Date", "Qty", "Product_Family"]]

    bars = (
        alt.Chart(df)
            .mark_bar()
            .encode(
            y="Qty:Q",
            color="Product_Family:N",
            tooltip=["Product_Family", "Qty"],
        )
            .interactive()
            .properties(width=550 / len(timeline) - 22, height=100)
    )

    chart_inventory = (
        alt.layer(bars, data=df)
            .facet(column="Date:N")
            .properties(title="Inventory")
    )

    # Plot shortage
    df = (
        planning.filter(like="late prod", axis=0)
            .copy()
            .rename(columns={"Solution": "Qty"})
            .reset_index()
    )

    df[["Date", "Order"]] = df["index"].str.split(",", expand=True)
    df["Date"] = df["Date"].str.split("[").str[1]
    df["Order"] = df["Order"].str.split("]").str[0]
    df = df[["Date", "Qty", "Order"]]

    models_list = cust_orders[['Order', 'Product_Family']]
    df = pd.merge(df, models_list, on='Order', how='inner')
    df = df[["Date", "Qty", "Product_Family"]]

    bars = (
        alt.Chart(df)
            .mark_bar()
            .encode(
            y="Qty:Q",
            color="Product_Family:N",
            tooltip=["Product_Family", "Qty"],
        )
            .interactive()
            .properties(width=550 / len(timeline) - 22, height=100)
    )

    chart_shortage = (
        alt.layer(bars, data=df)
            .facet(column="Date:N")
            .properties(title="Shortage")
    )

    chart = alt.vconcat(chart_inventory, chart_shortage)
    chart.save("Inventory_Shortage.html")

    dp.Report(
        '### Inventory_Shortage',
        dp.Plot(chart, caption="Inventory_Shortage")
    ).publish(name='Inventory_Shortage',
              description="Inventory_Shortage", open=True)


def print_planning(planning: pd.DataFrame) -> None:
    df = (
        planning.filter(like="plannedQty", axis=0)
            .copy()
            .rename(columns={"Solution": "Qty"})
            .reset_index()
    )
    df[["Date", "Customer_Order", "Line"]] = df["index"].str.split(",", expand=True)
    df["Date"] = df["Date"].str.split("[").str[1]
    df["Line"] = df["Line"].str.split("]").str[0]
    df = df[["Date", "Line", "Qty", "Customer_Order"]]

    df.to_csv(r"Planning_model4_list.csv", index=True)
    df.pivot_table(
        values="Qty", index="Customer_Order", columns=["Date", "Line"]
    ).to_csv(r"Planning_model4v2.csv", index=True)


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

# Get orders
customer_orders = pd.read_excel("Customer_orders.xlsx")

# Get cycle times
capacity = pd.read_excel("Constraints.xlsx", sheet_name="8h capacity").set_index("Line")
cycle_time = capacity.rdiv(8)


def check_duplicates(list_to_check):
    if len(list_to_check) == len(set(list_to_check)):
        return
    else:
        print("Duplicate order, please check the requirements file")
        exit()
        return


order_list = customer_orders["Order"].to_list()
check_duplicates(order_list)

# Create cycle times dictionnary
customer_orders = customer_orders.merge(
    cycle_time, left_on="Product_Family", right_index=True
)

customer_orders["Delivery_Date"] = pd.to_datetime(
    customer_orders["Delivery_Date"]
).dt.strftime("%Y/%m/%d")
customer_orders = customer_orders.sort_values(by=["Delivery_Date", "Order"])

cycle_times = {
    (order, line): customer_orders[line][customer_orders.Order == order].item()
    for order in order_list
    for line in lines
}

# Define calendar
start_date = datetime.datetime.strptime(
    customer_orders["Delivery_Date"].min(), "%Y/%m/%d"
)
end_date = datetime.datetime.strptime(
    customer_orders["Delivery_Date"].max(), "%Y/%m/%d"
)

date_modified = start_date
calendar = [start_date.strftime("%Y/%m/%d")]

while date_modified < end_date:
    date_modified += datetime.timedelta(days=1)
    calendar.append(date_modified.strftime("%Y/%m/%d"))

# Create daily requirements dictionnary
daily_requirements = {}
for day in calendar:
    for order in order_list:
        try:
            daily_requirements[(day, order)] = customer_orders[
                (customer_orders.Order == order)
                & (customer_orders.Delivery_Date == day)
                ]["Quantity"].item()
        except ValueError:
            daily_requirements[(day, order)] = 0

# Optimize planning
solution = optimize_planning(
    calendar,
    lines,
    daily_requirements,
    reg_costs_per_line,
    ot_costs_per_line,
    we_costs_per_line,
    storage_cost,
    order_list,
    cycle_times,
    late_prod_cost,
)

# Plot the new planning
plot_load(solution, daily_requirements, calendar)
print_planning(solution)
plot_planning(solution, daily_requirements, calendar)
plot_inventory(solution, calendar, customer_orders)
