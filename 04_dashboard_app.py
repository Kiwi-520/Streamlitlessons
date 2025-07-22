

# Step-by-step approach:
# 1. Import libraries (streamlit, pandas, numpy, plotly.express)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import date

st.header("Data Dashboard")
# 2. Create sample data

dates = pd.date_range('2024-01-01', periods=100, freq = 'D')

categories = ['Electronics', 'Clothing', 'Books', 'Sport']

data={
        'date':np.random.choice(dates,100),
        'sales':np.random.randint(100,1000,100),
        'categories':np.random.choice(categories, 100)
}

df = pd.DataFrame(data)

if st.button('Show DataFrame:'):
        st.dataframe(df)
        
# 3. Add user controls (widgets)

# data range

df['date'] = pd.to_datetime(df['date']).dt.date

min_date = df['date'].min()
max_date = df['date'].max()

date_range = st.date_input('Select date range',(min_date,max_date))

filtered_date_df = df[
        (df['date'] <= date_range[1]) & 
        (df['date'] >= date_range[0])
]

if st.button('Show Date Filtered DataFrame:'):
        st.header('Date Filtered DataFrame')
        st.dataframe(filtered_date_df)


# Multiselect Categories
categories_choice = st.multiselect("Choose multiple Categories",categories)

filtered_category_df = df[df['categories'].isin(categories_choice)]

if st.button('Show CategoryFiltered Data frame:'):
        st.header('Category Filtered DataFrame')
        st.dataframe(filtered_category_df)

# Sales slider

min_sale, max_sale = st.slider(
        'Select range for sales',
        min_value = 100,
        max_value = 999,
        value=(150, 800)
)

filtered_sales_df = df[(df['sales'] > min_sale) & (df['sales'] < max_sale)]

if st.button('Show Sales filtered DataFrame:'):
        st.header('Sales Filtered DataFrame')
        st.dataframe(filtered_sales_df)

# 4. Filter data based on user inputs

filtered_all_df = df[
        (df['date'] <= date_range[1]) & 
        (df['date'] >= date_range[0]) &
        df['categories'].isin(categories_choice) &
        (df['sales'] > min_sale) & (df['sales'] < max_sale)
]


if st.button('Show All filtered DataFrame'):
    st.subheader('All Filtered DataFrame')
    st.dataframe(filtered_all_df)

# 5. Display metrics and charts

# Choose Chart type

chart_type = st.radio("Choose chart type",['Line Chart','Scatter Chart','Area Chart','Bar Chart','Histogram','Pie Chart'])

# # Line chart

df_sales_sort = df.sort_values('sales',ascending = True)

fig1 = px.line(y = df_sales_sort['date'], x = df_sales_sort['sales'], title = 'Sales Over Time')
# st.plotly_chart(fig1)

# Bar chart

df_bar = df.groupby('categories')['sales'].sum().reset_index()

fig2 = px.bar(df_bar, x = df_bar['categories'], y = df_bar['sales'], title = 'Total Sales by Category')
# st.plotly_chart(fig2)

# Area chart

fig3 = px.area(x = df_sales_sort['date'], y = df_sales_sort['sales'], title = 'Sales Area Chart')
# st.plotly_chart(fig3)

# Scatter plot

df_date_sort = df.sort_values('date', ascending = False)

fig4 = px.scatter(x = df_date_sort['date'], y = df_date_sort['sales'], color = df_date_sort['categories'], title = 'Sales Scatter Plot')
# st.plotly_chart(fig4)

# Pie chart

proportions = df['categories'].value_counts(normalize=True)
df_pie = proportions.reset_index()
df_pie.columns = ['categories','proportions']

fig5 = px.pie(df_pie, names = 'categories', values = 'proportions', title = 'Category Proportion')
# st.plotly_chart(fig5)

# Histogram

fig6  = px.histogram(df, x='sales',nbins = 20, title='Sales Distribution')
# st.plotly_chart(fig6)

if chart_type == 'Line Chart':
        st.plotly_chart(fig1)
elif chart_type == 'Bar Chart':
        st.plotly_chart(fig2)
elif chart_type == 'Scatter Chart':
        st.plotly_chart(fig4)
elif chart_type == 'Area Chart':
        st.plotly_chart(fig3)
elif chart_type == 'Pie Chart':
        st.plotly_chart(fig5)
elif chart_type == 'Histogram':
        st.plotly_chart(fig6)



# 6. Make it interactive and beautiful!

# Remember to test frequently with: streamlit run 04_data_dashboard.py
