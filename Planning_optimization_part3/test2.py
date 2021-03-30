# Import required packages
import pandas as pd
import gurobipy
import datetime
from typing import List, Dict
import altair as alt


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

#print(calendar)
#print(MO_df)
#print(MO_df['Planned_Finish_Date'])
#print(MO_df['Planned_Finish_Date'].min())
#print(MO_df['Planned_Finish_Date'].max())

sdate = datetime.datetime.strptime( MO_df['Planned_Finish_Date'].min() , '%Y/%m/%d' )
edate = datetime.datetime.strptime( MO_df['Planned_Finish_Date'].max() , '%Y/%m/%d' )


date_modified=sdate
list=[sdate.strftime('%Y/%m/%d') ]


while date_modified < edate:
    date_modified += datetime.timedelta(days=1)
    list.append( date_modified.strftime('%Y/%m/%d') )


print(list)


print(MO_list)
print(set(MO_list))


def checkIfDuplicates(listOfElems):
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        print("Duplicate MO, please check the requirements file")
        exit()
        return True

checkIfDuplicates(MO_list)