import streamlit as st
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os


# Write directly to the app
st.title("Superstore Analytics Hub")
st.write(
    """Uncovering Retail Trends"""
)

ctx = snowflake.connector.connect(
    user='YASH2599',
    password='Nyspd015#',
    account='dqhibmr-dlb10609',
    role = 'ACCOUNTADMIN',
    warehouse='COMPUTE_WH',
    database='ADT_PROJECT',
    schema ='SUPERSTORE')

cs = ctx.cursor()

sql = """SELECT * FROM SUPERSTORE_US;"""
cs.execute(sql)
results = cs.fetchall()

columns = [desc[0] for desc in cs.description]

df2 = pd.DataFrame(results, columns=columns)

#st.dataframe(df2)


#st.dataframe(results)
#df2 = pd.DataFrame(results)
#st.write(df2)

#sql = f"select * from ADT_PROJECT2.SUPERSTORE.SUPERSTORE_US"
#df2 = session.sql(sql).collect()
#df2 = pd.DataFrame(df2)

sales_profits_by_state = df2.groupby('STATEPROVINCE').agg({
    'SALES': 'sum',
    'PROFIT': 'sum'
})

sales_profits_by_state = sales_profits_by_state.sort_values(by='SALES', ascending=False).reset_index()

# Select the top 10 rows
top_10_sales_profits_by_state = sales_profits_by_state.head(10)
st.title('Insight into Top 10 States in the Business')
st.table(top_10_sales_profits_by_state)


df2['ORDERDATE'] = pd.to_datetime(df2['ORDERDATE'])
df2['TOTAL SALES'] = df2.groupby('ORDERDATE')['SALES'].transform('sum')
df2['TOTAL PROFIT'] = df2.groupby('ORDERDATE')['PROFIT'].transform('sum')
df2['TOTAL DISCOUNT'] = df2.groupby('ORDERDATE')['DISCOUNT'].transform('sum')

st.title('Sales, Discount, and Profit Over Time')
selected_metric = st.selectbox('Select Metric', ['TOTAL SALES', 'TOTAL PROFIT', 'TOTAL DISCOUNT', 'ALL METRICS'])
if selected_metric == 'ALL METRICS':
    st.line_chart(df2.set_index('ORDERDATE')[['TOTAL SALES', 'TOTAL PROFIT', 'TOTAL DISCOUNT']])
else:
    st.line_chart(df2.set_index('ORDERDATE')[selected_metric])


# Calculate total sales, profit, and discount per product category
sales_by_category = df2.groupby('CATEGORY')['SALES'].sum().reset_index()
profit_by_category = df2.groupby('CATEGORY')['PROFIT'].sum().reset_index()
discount_by_category = df2.groupby('CATEGORY')['DISCOUNT'].sum().reset_index()

# Visualization - Dropdown
st.title('Sales, Profit, and Discount Distribution Across Product Categories')

# Dropdown to select the chart type
chart_type = st.selectbox('Select Chart Type', ['Sales Distribution', 'Profit Distribution', 'Discount Distribution'])

# Display the selected chart
if chart_type == 'Sales Distribution':
    st.write('### Sales Distribution Across Product Categories')
    # Create a pie chart for sales using Matplotlib
    fig_sales, ax_sales = plt.subplots()
    ax_sales.pie(sales_by_category['SALES'], labels=sales_by_category['CATEGORY'], autopct='%1.1f%%', startangle=90)
    ax_sales.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig_sales)

elif chart_type == 'Profit Distribution':
    st.write('### Profit Distribution Across Product Categories')
    # Create a pie chart for profit using Matplotlib
    fig_profit, ax_profit = plt.subplots()
    ax_profit.pie(profit_by_category['PROFIT'], labels=profit_by_category['CATEGORY'], autopct='%1.1f%%', startangle=90)
    ax_profit.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig_profit)

elif chart_type == 'Discount Distribution':
    st.write('### Discount Distribution Across Product Categories')
    # Create a pie chart for discount using Matplotlib
    fig_discount, ax_discount = plt.subplots()
    ax_discount.pie(discount_by_category['DISCOUNT'], labels=discount_by_category['CATEGORY'], autopct='%1.1f%%', startangle=90)
    ax_discount.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig_discount)





customer_category_distribution = df2['CATEGORY'].value_counts().reset_index()
customer_category_distribution.columns = ['CATEGORY', 'Number of Customers']

# Visualization - Bar chart
st.title('Distribution of Customers Across Category')

# Create a bar chart using Plotly Express with different colors for each category
fig_bar = px.bar(customer_category_distribution, x='CATEGORY', y='Number of Customers',
                 labels={'Number of Customers': 'Number of Customers'},
                 color='CATEGORY')  

# Display the plot in Streamlit app
st.plotly_chart(fig_bar)

# Calculate the distribution of 'SUBCATEGORY' within each category
subcategory_distribution = df2.groupby(['CATEGORY', 'SUBCATEGORY']).size().reset_index(name='Count')

# Visualization - Dropdown and Bar Plot
st.title('Distribution of Subcategories Within Each Category')

# Dropdown to select a category
selected_category = st.selectbox('Select a Category', subcategory_distribution['CATEGORY'].unique())

# Filter data for the selected category
selected_category_data = subcategory_distribution[subcategory_distribution['CATEGORY'] == selected_category]

# Sort data by count in descending order
selected_category_data = selected_category_data.sort_values(by='Count', ascending=False)

# Create a bar plot for the selected category with different colors
fig_bar = px.bar(selected_category_data, x='SUBCATEGORY', y='Count',
                 labels={'Count': 'Number of Products'},
                 title=f'Distribution of Subcategories in {selected_category}',
                 color='SUBCATEGORY', 
                 color_discrete_sequence=px.colors.qualitative.Set1)
fig_bar.update_layout(showlegend=False)
st.plotly_chart(fig_bar)



shipping_mode_distribution = df2['SHIPMODE'].value_counts().reset_index()
shipping_mode_distribution.columns = ['SHIPMODE', 'Number of Orders']

# Visualization - Bar chart
st.title('Distribution of Orders Across Different Shipping Modes')

# Create a bar chart using Plotly Express
fig_bar = px.bar(shipping_mode_distribution, x='SHIPMODE', y='Number of Orders',
                 labels={'Number of Orders': 'Number of Orders'},
                 title='Distribution of Orders Across Different Shipping Modes',
                color='SHIPMODE')

fig_bar.update_layout(showlegend=False)
st.plotly_chart(fig_bar)




df2['ORDERDATE'] = pd.to_datetime(df2['ORDERDATE'])
df2['SHIPDATE'] = pd.to_datetime(df2['SHIPDATE'])

# Calculate the time taken between order and shipment
df2['TimeTaken'] = (df2['SHIPDATE'] - df2['ORDERDATE']).dt.days

# Visualization - Histogram with lines surrounding each bar
st.title('Time Taken Between Order and Shipment (in days)')

# Create a histogram using Plotly Express
fig_hist = px.histogram(df2, x='TimeTaken',
                        labels={'TimeTaken': 'Time Taken Between Order and Shipment (in days)'},
                        title='Distribution of Time Taken Between Order and Shipment')  # You can adjust the number of bins as needed

fig_hist.update_traces(marker_line_width=1, marker_line_color="black", opacity=0.7)
st.plotly_chart(fig_hist)




st.title('Top N Prducts Based on Selected Matrices')
top_n = st.number_input('Enter the number of top products', min_value=1, value=10)

# Dropdown to select a metric (Sales or Profit)
selected_metric = st.selectbox('Select a Metric', ['SALES', 'PROFIT'])

# Calculate the top N products based on the selected metric
top_n_products = df2.groupby('PRODUCTNAME')[selected_metric].sum().nlargest(top_n).reset_index()

# Rename columns for clarity
top_n_products = top_n_products.rename(columns={
    'PRODUCTNAME': 'Product Name',
    selected_metric: f'Total {selected_metric.capitalize()}'
})

# Display the top N products in a table
st.table(top_n_products)


st.title('Top N Customers Based on Total Orders')
top_n_customers = st.number_input('Enter the number of top customers', min_value=1, value=10)

# Calculate the top N customers based on CUSTOMERID
top_n_customers_df = df2.groupby('CUSTOMERID').agg({
    'CUSTOMERNAME': 'first',
    'STATEPROVINCE': 'first',
    'DISCOUNT': 'sum',
    'ORDERID': 'nunique'
}).nlargest(top_n_customers, 'ORDERID').reset_index()

# Rename columns for clarity
top_n_customers_df = top_n_customers_df.rename(columns={
    'CUSTOMERID': 'Customer ID',
    'CUSTOMERNAME': 'Customer Name',
    'STATEPROVINCE': 'State',
    'ORDERID': 'Total Orders',
    'DISCOUNT': 'Total Discount Received (%)'
})
st.table(top_n_customers_df)


st.title("Delete a Product")

# Display unique products
unique_products = df2['PRODUCTNAME'].unique()
selected_product = st.selectbox("Select a Product to Delete", unique_products)

selected_product_info = df2[df2['PRODUCTNAME'] == selected_product][['PRODUCTID', 'PRODUCTNAME', 'CATEGORY', 'SUBCATEGORY']]
selected_product_info = df2[df2['PRODUCTNAME'] == selected_product][['PRODUCTID', 'PRODUCTNAME', 'CATEGORY', 'SUBCATEGORY']]
unique_selected_product_info = selected_product_info.drop_duplicates()
st.write(f"Information about {selected_product}:")
st.write(unique_selected_product_info)

# Button to delete the selected product
if st.button("Delete Selected Product"):
    delete_query = f"DELETE FROM SUPERSTORE_US WHERE PRODUCTNAME = '{selected_product}'"
    cs.execute(delete_query)
    ctx.commit()
    #df2 = df2[df2['PRODUCTNAME'] != selected_product]
    st.success(f"Product '{selected_product}' deleted successfully!")
     
st.write("Updated Data:")
sql2 = """SELECT * FROM SUPERSTORE_US;"""
cs.execute(sql2)
results2 = cs.fetchall()

columns = [desc[0] for desc in cs.description]

df2 = pd.DataFrame(results, columns=columns)
st.dataframe(df2[['PRODUCTID', 'PRODUCTNAME', 'CATEGORY', 'SUBCATEGORY']])


st.title("Update Product Name")

# Display unique products
unique_products = df2['PRODUCTNAME'].unique()
selected_product = st.selectbox("Select a Product", unique_products)

selected_product_info = df2[df2['PRODUCTNAME'] == selected_product][['PRODUCTID', 'PRODUCTNAME', 'CATEGORY', 'SUBCATEGORY']]
unique_selected_product_info = selected_product_info.drop_duplicates()
st.write(f"Information about {selected_product}:")
st.write(unique_selected_product_info[['PRODUCTID', 'PRODUCTNAME', 'CATEGORY', 'SUBCATEGORY']])

new_product_name = st.text_input("New Product Name:", value=selected_product)
# Button to update product name for the selected product

if st.button("Update Product Name for Selected Product"):
    # Execute the UPDATE statement
    update_query = f"UPDATE SUPERSTORE_US SET PRODUCTNAME = '{new_product_name}' WHERE PRODUCTNAME = '{selected_product}'"
    cs.execute(update_query)

    # Commit the transaction
    ctx.commit()

    st.success(f"Product name for '{selected_product}' updated to '{new_product_name}' successfully!")

# Display remaining data after update
st.write("Updated Data:")
sql3 = """SELECT * FROM SUPERSTORE_US;"""
cs.execute(sql3)
results3 = cs.fetchall()

columns = [desc[0] for desc in cs.description]

df3 = pd.DataFrame(results3, columns=columns)
st.dataframe(df3[['PRODUCTID', 'PRODUCTNAME', 'CATEGORY', 'SUBCATEGORY']])