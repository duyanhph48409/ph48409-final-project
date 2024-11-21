import pandas as pd

df = pd.read_csv('us-population-2010-2019.csv')
df = pd.melt(df, id_vars=['states', 'id'], var_name='year', value_name='population')

#Chuyển đổi kiểu dữ liệu
df['states'] = df['states'].astype(str)
df['id'] = df['id'].astype(int)
df['year'] = df['year'].astype(int)
df['population'] = df['population'].str.replace(',', '').astype(int)

#Lọc theo năm
selected_year = 2015
df_selected_year = df[df['year'] == selected_year]
df_selected_year.head()

# Sắp xếp DataFrame theo cột 'population' giảm dần
df_selected_year = df_selected_year.sort_values(by='population', ascending=False)

# Hiển thị DataFrame
df_selected_year

def diff_population_previous(input_df, input_year):
    # Lọc dữ liệu của năm hiện tại và năm trước
    df_selected_year = input_df[input_df['year'] == input_year]
    df_previous_year = input_df[input_df['year'] == input_year - 1]

    # Merge hai DataFrame dựa trên cột nhận dạng, ví dụ: 'state' và 'id'
    df_merged = pd.merge(
        df_selected_year,
        df_previous_year,
        on=['states', 'id'],  # Cột nhận dạng
        suffixes=('_current', '_previous'),
        how='left'
    )

    # Tính sự khác biệt dân số
    df_merged['diff_population'] = (
        df_merged['population_current'] - df_merged['population_previous']
    )

    # Trả về kết quả chỉ với các cột cần thiết
    return df_merged[['states', 'id', 'year_current', 'population_current', 'diff_population']]

diff_population_previous(df, 2014)

#Lấy danh sách các bang dân số bị giảm so với năm trước trong năm 2014
df_diff_2014_2013 = diff_population_previous(df, 2014)
df_decrease_2014_2013 = df_diff_2014_2013[df_diff_2014_2013['diff_population'] < 0]
df_decrease_2014_2013

#Tính phần trăm dân số trên tổng số bang
len(df_decrease_2014_2013) / len(df_diff_2014_2013) * 100

import altair as alt

state_order = df.groupby('states')['population'].max().sort_values(ascending=False).index.tolist()
heatmap = alt.Chart(df).mark_rect().encode(
    alt.X('states:O', title='Bang', sort=state_order),
    alt.Y('year:O', title='Năm', sort='ascending'),
    alt.Color('population:Q', title='Dân số', scale=alt.Scale(scheme='viridis'))
).properties(
    title='Mật độ dân số theo bang và năm'
)

heatmap

import matplotlib.pyplot as plt
import seaborn as sns

df['states'] = df['states'].str.strip()
# Group by năm
df_yearly = df.groupby('year')['population'].sum().reset_index()

# Vẽ biểu đồ
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_yearly, x='year', y='population', marker='o', linewidth=2.5)

# Tiêu đề và nhãn
plt.title('Tăng trưởng dân số Hoa Kỳ theo từng năm (2010-2019)', fontsize=14)
plt.xlabel('Năm', fontsize=12)
plt.ylabel('Dân số (người)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Hiển thị
plt.show()

# Lọc ra dân số của năm 2010 và 2019
df_2010_2019 = df[df['year'].isin([2010, 2019])]

# Pivot bảng để có dữ liệu dân số năm 2010 và 2019 cho từng bang
df_pivot = df_2010_2019.pivot(index='states', columns='year', values='population')

# Đổi tên cột năm thành chuỗi để phù hợp với yêu cầu của Altair
df_pivot.columns = df_pivot.columns.astype(str)

# Tính tỷ lệ tăng trưởng từ 2010 đến 2019
df_pivot['growth_rate'] = ((df_pivot['2019'] - df_pivot['2010']) / df_pivot['2010']) * 100

# Tạo biểu đồ bar cho tỷ lệ tăng trưởng
growth_chart = alt.Chart(df_pivot.reset_index()).mark_bar().encode(
    alt.X('growth_rate:Q', title='Tỷ lệ tăng trưởng (%)'),
    alt.Y('states:N', title='Bang'),
    color='growth_rate:Q'
).properties(
    width=600,
    height=400
)

# Thêm giá trị vào các cột
growth_chart = growth_chart.encode(
    text='growth_rate:Q'
)

growth_chart
