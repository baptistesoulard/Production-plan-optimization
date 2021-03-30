# Import required packages
import pandas as pd
import gurobipy
import datetime
from typing import List, Dict
import altair as alt





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


#sfgdfgdfgfdgfdgfd


source = pd.Series(daily_requirements).rename_axis(["Date", "MO_No"]).reset_index(name="Qty")


print(source.columns)
print(source)
print(source.groupby(['Date']).sum())

chart_need = (
    alt.Chart(source)
        .mark_bar()
        .encode(
        y=alt.Y("Qty", axis=alt.Axis(grid=False)),
        column=alt.Column("Date:N"),
        color="MO_No:N",
        tooltip=['MO_No', 'Qty']
    ).interactive()
        .properties(
        width=600 / len(calendar) - 22,
        height=90,
        title="test",
    )
)

source = source.groupby(['Date']).sum()
source['Date'] = source.index
source = source.reset_index(drop=True)

chart_need = (
    alt.Chart(source)
        .mark_bar()
        .encode(
        y=alt.Y("Qty", axis=alt.Axis(grid=False)),
        column=alt.Column("Date:N"),
        tooltip=['Qty']
    ).interactive()
        .properties(
        width=600 / len(calendar) - 22,
        height=90,
        title="Requirement",
    )
)

chart = alt.vconcat(chart_need, chart_need2)
chart.save("test.html")