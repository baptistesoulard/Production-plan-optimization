\ Model Optimize production planning
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  Labor_cost[2020/7/13,Line_1] + Labor_cost[2020/7/13,Line_2]
   + Labor_cost[2020/7/13,Line_3] + Labor_cost[2020/7/14,Line_1]
   + Labor_cost[2020/7/14,Line_2] + Labor_cost[2020/7/14,Line_3]
   + Labor_cost[2020/7/15,Line_1] + Labor_cost[2020/7/15,Line_2]
   + Labor_cost[2020/7/15,Line_3] + Labor_cost[2020/7/16,Line_1]
   + Labor_cost[2020/7/16,Line_2] + Labor_cost[2020/7/16,Line_3]
   + Labor_cost[2020/7/17,Line_1] + Labor_cost[2020/7/17,Line_2]
   + Labor_cost[2020/7/17,Line_3] + Labor_cost[2020/7/18,Line_1]
   + Labor_cost[2020/7/18,Line_2] + Labor_cost[2020/7/18,Line_3]
   + Labor_cost[2020/7/19,Line_1] + Labor_cost[2020/7/19,Line_2]
   + Labor_cost[2020/7/19,Line_3]
Subject To
 Link_total_hours_-_requirement[2020/7/13]: Total_hours[2020/7/13,Line_1]
   + Total_hours[2020/7/13,Line_2] + Total_hours[2020/7/13,Line_3] = 30
 Link_total_hours_-_requirement[2020/7/14]: Total_hours[2020/7/14,Line_1]
   + Total_hours[2020/7/14,Line_2] + Total_hours[2020/7/14,Line_3] = 10
 Link_total_hours_-_requirement[2020/7/15]: Total_hours[2020/7/15,Line_1]
   + Total_hours[2020/7/15,Line_2] + Total_hours[2020/7/15,Line_3] = 34
 Link_total_hours_-_requirement[2020/7/16]: Total_hours[2020/7/16,Line_1]
   + Total_hours[2020/7/16,Line_2] + Total_hours[2020/7/16,Line_3] = 25
 Link_total_hours_-_requirement[2020/7/17]: Total_hours[2020/7/17,Line_1]
   + Total_hours[2020/7/17,Line_2] + Total_hours[2020/7/17,Line_3] = 23
 Link_total_hours_-_requirement[2020/7/18]: Total_hours[2020/7/18,Line_1]
   + Total_hours[2020/7/18,Line_2] + Total_hours[2020/7/18,Line_3] = 24
 Link_total_hours_-_requirement[2020/7/19]: Total_hours[2020/7/19,Line_1]
   + Total_hours[2020/7/19,Line_2] + Total_hours[2020/7/19,Line_3] = 25
 Link_total_hours_-_reg/ot_hours[2020/7/13,Line_1]:
   Total_hours[2020/7/13,Line_1] + [
   - Working_hours[2020/7/13,Line_1] * Open_status[2020/7/13,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/13,Line_2]:
   Total_hours[2020/7/13,Line_2] + [
   - Working_hours[2020/7/13,Line_2] * Open_status[2020/7/13,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/13,Line_3]:
   Total_hours[2020/7/13,Line_3] + [
   - Working_hours[2020/7/13,Line_3] * Open_status[2020/7/13,Line_3] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/14,Line_1]:
   Total_hours[2020/7/14,Line_1] + [
   - Working_hours[2020/7/14,Line_1] * Open_status[2020/7/14,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/14,Line_2]:
   Total_hours[2020/7/14,Line_2] + [
   - Working_hours[2020/7/14,Line_2] * Open_status[2020/7/14,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/14,Line_3]:
   Total_hours[2020/7/14,Line_3] + [
   - Working_hours[2020/7/14,Line_3] * Open_status[2020/7/14,Line_3] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/15,Line_1]:
   Total_hours[2020/7/15,Line_1] + [
   - Working_hours[2020/7/15,Line_1] * Open_status[2020/7/15,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/15,Line_2]:
   Total_hours[2020/7/15,Line_2] + [
   - Working_hours[2020/7/15,Line_2] * Open_status[2020/7/15,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/15,Line_3]:
   Total_hours[2020/7/15,Line_3] + [
   - Working_hours[2020/7/15,Line_3] * Open_status[2020/7/15,Line_3] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/16,Line_1]:
   Total_hours[2020/7/16,Line_1] + [
   - Working_hours[2020/7/16,Line_1] * Open_status[2020/7/16,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/16,Line_2]:
   Total_hours[2020/7/16,Line_2] + [
   - Working_hours[2020/7/16,Line_2] * Open_status[2020/7/16,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/16,Line_3]:
   Total_hours[2020/7/16,Line_3] + [
   - Working_hours[2020/7/16,Line_3] * Open_status[2020/7/16,Line_3] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/17,Line_1]:
   Total_hours[2020/7/17,Line_1] + [
   - Working_hours[2020/7/17,Line_1] * Open_status[2020/7/17,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/17,Line_2]:
   Total_hours[2020/7/17,Line_2] + [
   - Working_hours[2020/7/17,Line_2] * Open_status[2020/7/17,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/17,Line_3]:
   Total_hours[2020/7/17,Line_3] + [
   - Working_hours[2020/7/17,Line_3] * Open_status[2020/7/17,Line_3] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/18,Line_1]:
   Total_hours[2020/7/18,Line_1] + [
   - Working_hours[2020/7/18,Line_1] * Open_status[2020/7/18,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/18,Line_2]:
   Total_hours[2020/7/18,Line_2] + [
   - Working_hours[2020/7/18,Line_2] * Open_status[2020/7/18,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/18,Line_3]:
   Total_hours[2020/7/18,Line_3] + [
   - Working_hours[2020/7/18,Line_3] * Open_status[2020/7/18,Line_3] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/19,Line_1]:
   Total_hours[2020/7/19,Line_1] + [
   - Working_hours[2020/7/19,Line_1] * Open_status[2020/7/19,Line_1] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/19,Line_2]:
   Total_hours[2020/7/19,Line_2] + [
   - Working_hours[2020/7/19,Line_2] * Open_status[2020/7/19,Line_2] ] = 0
 Link_total_hours_-_reg/ot_hours[2020/7/19,Line_3]:
   Total_hours[2020/7/19,Line_3] + [
   - Working_hours[2020/7/19,Line_3] * Open_status[2020/7/19,Line_3] ] = 0
 Link_labor_cost_-_working_hours[2020/7/13,Line_1]:
   Labor_cost[2020/7/13,Line_1] + [
   - 245 Open_status[2020/7/13,Line_1] * Total_hours[2020/7/13,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/13,Line_2]:
   Labor_cost[2020/7/13,Line_2] + [
   - 315 Open_status[2020/7/13,Line_2] * Total_hours[2020/7/13,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/13,Line_3]:
   Labor_cost[2020/7/13,Line_3] + [
   - 245 Open_status[2020/7/13,Line_3] * Total_hours[2020/7/13,Line_3] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/14,Line_1]:
   Labor_cost[2020/7/14,Line_1] + [
   - 245 Open_status[2020/7/14,Line_1] * Total_hours[2020/7/14,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/14,Line_2]:
   Labor_cost[2020/7/14,Line_2] + [
   - 315 Open_status[2020/7/14,Line_2] * Total_hours[2020/7/14,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/14,Line_3]:
   Labor_cost[2020/7/14,Line_3] + [
   - 245 Open_status[2020/7/14,Line_3] * Total_hours[2020/7/14,Line_3] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/15,Line_1]:
   Labor_cost[2020/7/15,Line_1] + [
   - 245 Open_status[2020/7/15,Line_1] * Total_hours[2020/7/15,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/15,Line_2]:
   Labor_cost[2020/7/15,Line_2] + [
   - 315 Open_status[2020/7/15,Line_2] * Total_hours[2020/7/15,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/15,Line_3]:
   Labor_cost[2020/7/15,Line_3] + [
   - 245 Open_status[2020/7/15,Line_3] * Total_hours[2020/7/15,Line_3] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/16,Line_1]:
   Labor_cost[2020/7/16,Line_1] + [
   - 245 Open_status[2020/7/16,Line_1] * Total_hours[2020/7/16,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/16,Line_2]:
   Labor_cost[2020/7/16,Line_2] + [
   - 315 Open_status[2020/7/16,Line_2] * Total_hours[2020/7/16,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/16,Line_3]:
   Labor_cost[2020/7/16,Line_3] + [
   - 245 Open_status[2020/7/16,Line_3] * Total_hours[2020/7/16,Line_3] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/17,Line_1]:
   Labor_cost[2020/7/17,Line_1] + [
   - 245 Open_status[2020/7/17,Line_1] * Total_hours[2020/7/17,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/17,Line_2]:
   Labor_cost[2020/7/17,Line_2] + [
   - 315 Open_status[2020/7/17,Line_2] * Total_hours[2020/7/17,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/17,Line_3]:
   Labor_cost[2020/7/17,Line_3] + [
   - 245 Open_status[2020/7/17,Line_3] * Total_hours[2020/7/17,Line_3] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/18,Line_1]:
   Labor_cost[2020/7/18,Line_1] + [
   - 245 Open_status[2020/7/18,Line_1] * Total_hours[2020/7/18,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/18,Line_2]:
   Labor_cost[2020/7/18,Line_2] + [
   - 315 Open_status[2020/7/18,Line_2] * Total_hours[2020/7/18,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/18,Line_3]:
   Labor_cost[2020/7/18,Line_3] + [
   - 245 Open_status[2020/7/18,Line_3] * Total_hours[2020/7/18,Line_3] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/19,Line_1]:
   Labor_cost[2020/7/19,Line_1] + [
   - 245 Open_status[2020/7/19,Line_1] * Total_hours[2020/7/19,Line_1] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/19,Line_2]:
   Labor_cost[2020/7/19,Line_2] + [
   - 315 Open_status[2020/7/19,Line_2] * Total_hours[2020/7/19,Line_2] ]
   = 0
 Link_labor_cost_-_working_hours[2020/7/19,Line_3]:
   Labor_cost[2020/7/19,Line_3] + [
   - 245 Open_status[2020/7/19,Line_3] * Total_hours[2020/7/19,Line_3] ]
   = 0
Bounds
 7 <= Working_hours[2020/7/13,Line_1] <= 12
 7 <= Working_hours[2020/7/13,Line_2] <= 12
 7 <= Working_hours[2020/7/13,Line_3] <= 12
 7 <= Working_hours[2020/7/14,Line_1] <= 12
 7 <= Working_hours[2020/7/14,Line_2] <= 12
 7 <= Working_hours[2020/7/14,Line_3] <= 12
 7 <= Working_hours[2020/7/15,Line_1] <= 12
 7 <= Working_hours[2020/7/15,Line_2] <= 12
 7 <= Working_hours[2020/7/15,Line_3] <= 12
 7 <= Working_hours[2020/7/16,Line_1] <= 12
 7 <= Working_hours[2020/7/16,Line_2] <= 12
 7 <= Working_hours[2020/7/16,Line_3] <= 12
 7 <= Working_hours[2020/7/17,Line_1] <= 12
 7 <= Working_hours[2020/7/17,Line_2] <= 12
 7 <= Working_hours[2020/7/17,Line_3] <= 12
 7 <= Working_hours[2020/7/18,Line_1] <= 12
 7 <= Working_hours[2020/7/18,Line_2] <= 12
 7 <= Working_hours[2020/7/18,Line_3] <= 12
 7 <= Working_hours[2020/7/19,Line_1] <= 12
 7 <= Working_hours[2020/7/19,Line_2] <= 12
 7 <= Working_hours[2020/7/19,Line_3] <= 12
 Total_hours[2020/7/13,Line_1] <= 12
 Total_hours[2020/7/13,Line_2] <= 12
 Total_hours[2020/7/13,Line_3] <= 12
 Total_hours[2020/7/14,Line_1] <= 12
 Total_hours[2020/7/14,Line_2] <= 12
 Total_hours[2020/7/14,Line_3] <= 12
 Total_hours[2020/7/15,Line_1] <= 12
 Total_hours[2020/7/15,Line_2] <= 12
 Total_hours[2020/7/15,Line_3] <= 12
 Total_hours[2020/7/16,Line_1] <= 12
 Total_hours[2020/7/16,Line_2] <= 12
 Total_hours[2020/7/16,Line_3] <= 12
 Total_hours[2020/7/17,Line_1] <= 12
 Total_hours[2020/7/17,Line_2] <= 12
 Total_hours[2020/7/17,Line_3] <= 12
 Total_hours[2020/7/18,Line_1] <= 12
 Total_hours[2020/7/18,Line_2] <= 12
 Total_hours[2020/7/18,Line_3] <= 12
 Total_hours[2020/7/19,Line_1] <= 12
 Total_hours[2020/7/19,Line_2] <= 12
 Total_hours[2020/7/19,Line_3] <= 12
Binaries
 Open_status[2020/7/13,Line_1] Open_status[2020/7/13,Line_2]
 Open_status[2020/7/13,Line_3] Open_status[2020/7/14,Line_1]
 Open_status[2020/7/14,Line_2] Open_status[2020/7/14,Line_3]
 Open_status[2020/7/15,Line_1] Open_status[2020/7/15,Line_2]
 Open_status[2020/7/15,Line_3] Open_status[2020/7/16,Line_1]
 Open_status[2020/7/16,Line_2] Open_status[2020/7/16,Line_3]
 Open_status[2020/7/17,Line_1] Open_status[2020/7/17,Line_2]
 Open_status[2020/7/17,Line_3] Open_status[2020/7/18,Line_1]
 Open_status[2020/7/18,Line_2] Open_status[2020/7/18,Line_3]
 Open_status[2020/7/19,Line_1] Open_status[2020/7/19,Line_2]
 Open_status[2020/7/19,Line_3]
Generals
 Working_hours[2020/7/13,Line_1] Working_hours[2020/7/13,Line_2]
 Working_hours[2020/7/13,Line_3] Working_hours[2020/7/14,Line_1]
 Working_hours[2020/7/14,Line_2] Working_hours[2020/7/14,Line_3]
 Working_hours[2020/7/15,Line_1] Working_hours[2020/7/15,Line_2]
 Working_hours[2020/7/15,Line_3] Working_hours[2020/7/16,Line_1]
 Working_hours[2020/7/16,Line_2] Working_hours[2020/7/16,Line_3]
 Working_hours[2020/7/17,Line_1] Working_hours[2020/7/17,Line_2]
 Working_hours[2020/7/17,Line_3] Working_hours[2020/7/18,Line_1]
 Working_hours[2020/7/18,Line_2] Working_hours[2020/7/18,Line_3]
 Working_hours[2020/7/19,Line_1] Working_hours[2020/7/19,Line_2]
 Working_hours[2020/7/19,Line_3] Total_hours[2020/7/13,Line_1]
 Total_hours[2020/7/13,Line_2] Total_hours[2020/7/13,Line_3]
 Total_hours[2020/7/14,Line_1] Total_hours[2020/7/14,Line_2]
 Total_hours[2020/7/14,Line_3] Total_hours[2020/7/15,Line_1]
 Total_hours[2020/7/15,Line_2] Total_hours[2020/7/15,Line_3]
 Total_hours[2020/7/16,Line_1] Total_hours[2020/7/16,Line_2]
 Total_hours[2020/7/16,Line_3] Total_hours[2020/7/17,Line_1]
 Total_hours[2020/7/17,Line_2] Total_hours[2020/7/17,Line_3]
 Total_hours[2020/7/18,Line_1] Total_hours[2020/7/18,Line_2]
 Total_hours[2020/7/18,Line_3] Total_hours[2020/7/19,Line_1]
 Total_hours[2020/7/19,Line_2] Total_hours[2020/7/19,Line_3]
End
