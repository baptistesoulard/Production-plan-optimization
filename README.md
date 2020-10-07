# Production Plan Optimization

### Introduction
This project aims at providing a solution for planning optimization.
The example shown here is a manufacturing company that need to optimize its daily production plan in order to reduce the costs.

More and more constraints are considered from Model 1 to Model 7, the most sophisticated. 
Here is a brief introduction of each of these models:
-- Part 1:
- Model 1: 
  Daily requirement in number of hours to allocate between 3 different production lines, on the same day. 
  Capacity is the same for each production line but not hourly cost. One production line can not be opened for less than 7 hours or more than 12 hours.
- Model 2:
  The concept of overtime and weekend extra cost is added. Hours worked from 8 to 12 hours are paid 50% higher and hours worked during weekends are paid double. 
- Model 3:
  In order to better optimize our planning, we now allow to plan the production in advance to reduce extra costs due to OT or weekends.
  Concept of storage cost is introduced.
  
### Requirements
- Python 3.8
- Poetry
- Gurobi Python installed with a valid license


### How to setup

```shell script
poetry install
```

### How to run


To run Model1:
```shell script
python Model1/Model1.py
```

To run Model2:
```shell script
python Model2/Model2.py
```
