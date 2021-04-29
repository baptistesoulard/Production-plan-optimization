import pandas as pd
import datetime
from typing import List, Dict

# Define hourly cost per line - regular, overtime and weekend
reg_costs_per_line = {"Line_1": 245, "Line_2": 315, "Line_3": 245}
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

# Get changeover
data = pd.read_csv("Planning_model4_list.csv")
x_qty = {
    (day, order, line): data['Qty'][data.Date == day][data.Line == line][data.Customer_Order == order].item()
    for day in calendar
    for order in order_list
    for line in lines
}



print(calendar)
print(order_list)
print(lines)

print(x_qty)