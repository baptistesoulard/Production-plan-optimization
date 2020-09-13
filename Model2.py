# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 15:09:01 2020

@author: soulba01
"""

## Import required packages
import pandas as pd
import gurobipy
from matplotlib import pyplot as plt
import datetime

######     INITIALIZE THE MODEL     #####

model = gurobipy.Model("Minimize cost")


######     DECISION VARIABLES     #####

# Calendar
days = ['2020/7/15', '2020/7/16', '2020/7/17', '2020/7/18', '2020/7/19', '2020/7/20', '2020/7/21']

# Weekdays / Weekends
weekdaysList = []
weekendList = []
for i in days:
    date = datetime.datetime.strptime(i, "%Y/%m/%d")
    if date.weekday() < 5:
        weekdaysList.append(i)
    else:
        weekendList.append(i)
    
# Production lines
lines = ['Curtain_C1', 'Curtain_C2', 'Curtain_C3']

# Production requirement (hours)
dayReq = [30, 10, 34, 23, 23, 24, 25]
dayRequirements = {d : dayReq[i] for i,d in enumerate (days)}

# Hourly cost per line - regular and overtime
regCost = [350, 300, 350]
regCostDict = {l : regCost[i] for i,l in enumerate(lines)}

OTCost= [1.5 * i for i in regCost]
OTCostDict = {l : OTCost[i] for i,l in enumerate(lines)}

# Load variables (hours) - regular and overtime
regHours = model.addVars(days, lines, lb = 7, ub = 8, vtype=gurobipy.GRB.INTEGER, name='regHours')
OTHours = model.addVars(days, lines, lb = 0, ub = 4, vtype=gurobipy.GRB.INTEGER, name='OTHours')

# Status of the line ( 0 = closed, 1 = opened)
lineOpening = model.addVars(days, lines, vtype=gurobipy.GRB.BINARY, name='Open')

# Variable total load (hours)
totalHours = model.addVars(days, lines, lb = 0, ub = 12, vtype=gurobipy.GRB.INTEGER, name='totalHours')

# Variable cost
x = model.addVars(days, lines, lb=0, vtype=gurobipy.GRB.CONTINUOUS, name='Cost')


######     CONSTRAINTS     #####
        
# Set the value of cost (hours * hourly cost)
costConstr = model.addConstrs((
    (x[(i, j)] == regHours[(i, j)]*regCostDict[j]*lineOpening[(i, j)] + OTHours[(i, j)]*OTCostDict[j]*lineOpening[(i, j)] for i in days for j in lines)
    ), name='costConstr')        
        
# Set the value of total load (regular + overtime)
hoursConstr = model.addConstrs((
    (totalHours[(i, j)] == (regHours[(i, j)] + OTHours[(i, j)])*lineOpening[(i, j)] for i in days for j in lines)
    ), name='total_hours_constr') 
        
# Constraint : requirement = load of the 3 lines
dayReqConstr = model.addConstrs((
    ((totalHours).sum(d, '*') == dayRequirements[d] for d in days)
     ), name='Requirements')
        

#####     DEFINE MODEL     #####

model.ModelSense = gurobipy.GRB.MINIMIZE

Cost = 0
Cost += (gurobipy.quicksum(x[(i, j)] for i in days for j in lines))


#####     SOLVE MODEL     #####

model.setObjective(Cost)

#model.write("Optimized_Scheduling.lp")
#file = open("Optimized_Scheduling.lp", 'r')
#print(file.read())
#file.close()

model.optimize()

print('Total cost = $' + str(model.ObjVal))


######     DISPLAY RESULTS     #####

sol = pd.DataFrame(data={'Solution':model.X}, index=model.VarName)
sol = sol.filter(like='totalHours', axis=0)

dashboard = pd.DataFrame(index = lines, columns = days)
for l in lines:
    for d in days:
        dashboard.at[l,d] = sol.loc['totalHours[' +str(d)+ ',' +str(l)+ ']'][0]
        
print(dashboard)


#####     GRAPH     #####

Load_Graph = dashboard.T
Load_Graph['Min capacity'] = 7
Load_Graph['Max capacity'] = 12

my_colors = ['skyblue', 'salmon', 'lightgreen']

_, ax = plt.subplots()
Load_Graph[['Min capacity', 'Max capacity']].plot(rot=90, ax=ax, 
                                                style=['b','b--'], linewidth=1)
Load_Graph.drop(['Min capacity', 'Max capacity'], axis=1).plot(kind='bar', 
                    title = 'Load in % per line',  ax=ax, color=my_colors)

ax.tick_params(axis="x", labelsize=7)
ax.tick_params(axis="y", labelsize=7)

plt.savefig('LoadwithOT.pdf', bbox_inches='tight')

#dashboard.copy().to_csv(r'C:/Users/soulba01/Desktop/Test_python/PlanningInteger.csv', index=True)
