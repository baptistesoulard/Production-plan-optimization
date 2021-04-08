
# Define daily requirement dataframe
customer_orders = customer_orders[["Order", "Quantity", "Delivery_Date"]]
customer_orders = customer_orders.append(
    pd.DataFrame(
        {
            "Order": ["temp" for _ in range(len(calendar))],
            "Delivery_Date": calendar,
        }
    )
)
customer_orders = customer_orders.pivot(
    index="Order", columns="Delivery_Date", values="Quantity"
)
customer_orders = customer_orders.drop("temp", axis=0).fillna(0)

daily_requirements = {
    (i, j): customer_orders[i][j] for i in calendar for j in order_list
}

print(daily_requirements)