# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:09:01 2020

@author: soulba01
"""

# Import required packages
import pandas as pd
import gurobipy
from matplotlib import pyplot as plt
from typing import List, Dict, Tuple


######     INITIALIZE THE MODEL     ######

model = gurobipy.Model("Optimize production planning")


######     INPUT     ######

# Define the daily requirement
CALENDAR: List[str] = ['2020/7/13', '2020/7/14', '2020/7/15',
                       '2020/7/16', '2020/7/17', '2020/7/18',
                       '2020/7/19']
DAY_REQ: List[int] = [30, 10, 34, 23, 23, 24, 25]
DAY_REQUIREMENTS: Dict[str, int] = {d: DAY_REQ[i] for i, d in enumerate(CALENDAR)}

# Define the hourly cost per line
LINES: List[str] = ['Curtain_C1', 'Curtain_C2', 'Curtain_C3']
COST_temp: List[int] = [350, 300, 350]
COST_LINE = {l : COST_temp[i] for i,l in enumerate(LINES)}


######     DECISION VARIABLES     ######

# Define time variables
hours = model.addVars(CALENDAR, LINES, lb=7, ub=12, vtype=gurobipy.GRB.INTEGER, name='Hours')
line_opening = model.addVars(CALENDAR, LINES, vtype=gurobipy.GRB.BINARY, name='Line opening')
total_hours = model.addVars(CALENDAR, LINES, lb=0, ub=12, vtype=gurobipy.GRB.INTEGER, name='Total hours')

model.addConstrs((
    (total_hours[(i, j)] == hours[(i, j)] * line_opening[(i, j)] for i in CALENDAR for j in LINES)
    ), name='total_hours_constr')

# Define cost variable
cost = model.addVars(CALENDAR, LINES, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name='Cost')

for i in CALENDAR:
    for j in LINES:
        cost[(i, j)] = total_hours[(i, j)]*COST_LINE[j]


######     CONSTRAINTS     ######

# Total requirement = total planned
model.addConstrs((
    ((total_hours).sum(d, '*') == DAY_REQUIREMENTS[d] for d in CALENDAR)
     ), name='Requirements')
        

######     DEFINE MODEL     ######

model.ModelSense = gurobipy.GRB.MINIMIZE

optimization_var = (gurobipy.quicksum(cost[(i, j)] for i in CALENDAR for j in LINES))

objective = 0
objective += optimization_var


#####     SOLVE MODEL     #####

model.setObjective(objective)

model.optimize()
print('Total cost = $' + str(model.ObjVal))


######     DISPLAY RESULTS     #####

sol = pd.DataFrame(data={'Solution': model.X}, index=model.VarName)

sol = sol.iloc[2*len(cost):3*len(cost)]

dashboard = pd.DataFrame(index=LINES, columns=CALENDAR)
for l in LINES:
    for c in CALENDAR:
        dashboard.at[l, c] = sol.loc['Total hours[' + str(c) + ',' + str(l) + ']'][0]
        
print(dashboard)

#####     GRAPH     #####

Load_Graph = dashboard.T
Load_Graph['Min capacity'] = 7
Load_Graph['Max capacity'] = 12

my_colors = ['skyblue', 'salmon', 'lightgreen']

_, ax = plt.subplots()
Load_Graph[['Min capacity', 'Max capacity']].plot(
    rot=90, ax=ax, style=['b', 'b--'], linewidth=1)

Load_Graph.drop(['Min capacity', 'Max capacity'], axis=1).plot(
    kind='bar', title='Load in h per line',  ax=ax, color=my_colors)

ax.tick_params(axis="x", labelsize=7)
ax.tick_params(axis="y", labelsize=7)

plt.savefig('Result_Model1.png', bbox_inches='tight', dpi=1200)
