!pip install matplotlib
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st  # Add streamlit import

df = pd.read_csv('us-population-2010-2019.csv')
df = pd.melt(df, id_vars=['states', 'id'], var_name='year', value_name='population')
df['states'] = df['states'].astype(str)
df['id'] = df['id'].astype(int)
df['year'] = df['year'].astype(int)
df['population'] = df['population'].str.replace(',', '').astype(int)

# Lọc theo năm
selected_year = 2015
df_selected_year = df[df['year'] == selected_year]
df_selected_year = df_selected_year.sort_values(by='population', ascending=False)

# Tính sự khác biệt dân số
def diff_population_previous(input_df, input_year):
    df_selected_year = input_df[input_df['year'] == input_year]
    df_previous_year = input_df[input_df['year'] == input_year - 1]
    df_merged = pd.merge(
        df_selected_year,
        df_previous_year,
        on=['states', 'id'],  # Cột nhận dạng
        suffixes=('_current', '_previous'),
        how='left'
    )
    df_merged['diff_population'] = (
        df_merged['population_current'] - df_merged['population_previous']
    )
    return df_merged[['states', 'id', 'year_current', 'population_current', 'diff_population']]

df_diff_2014_2013 = diff_population_previous(df, 2014)
df_decrease_2014_2013 = df_diff_2014_2013[df_diff_2014_2013['diff_population'] < 0]

# Streamlit display for the Altair chart
state_order = df.groupby('states')['population'].max().sort_values(ascending=False).index.tolist()
heatmap = alt.Chart(df).mark_rect().encode(
    alt.X('states:O', title='Bang', sort=state_order),
    alt.Y('year:O', title='Năm', sort='ascending'),
    alt.Color('population:Q', title='Dân số', scale=alt.Scale(scheme='viridis'))
).properties(
    title='Mật độ dân số theo bang và năm'
)

st.write(heatmap)  # Displaying the Altair chart with Streamlit

# Seaborn Lineplot
df['states'] = df['states'].str.strip()
df_yearly = df.groupby('year')['population'].sum().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(data=df_yearly, x='year', y='population', marker='o', linewidth=2.5)
plt.title('Tăng trưởng dân số Hoa Kỳ theo từng năm (2010-2019)', fontsize=14)
plt.xlabel('Năm', fontsize=12)
plt.ylabel('Dân số (người)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

st.pyplot()  # This will display the Matplotlib chart in Streamlit

# Pivot and Growth Rate
df_2010_2019 = df[df['year'].isin([2010, 2019])]
df_pivot = df_2010_2019.pivot(index='states', columns='year', values='population')
df_pivot.columns = df_pivot.columns.astype(str)
df_pivot['growth_rate'] = ((df_pivot['2019'] - df_pivot['2010']) / df_pivot['2010']) * 100

growth_chart = alt.Chart(df_pivot.reset_index()).mark_bar().encode(
    alt.X('growth_rate:Q', title='Tỷ lệ tăng trưởng (%)'),
    alt.Y('states:N', title='Bang'),
    color='growth_rate:Q'
).properties(
    width=600,
    height=400
)

growth_chart = growth_chart.encode(
    text='growth_rate:Q'
)

st.write(growth_chart) 
