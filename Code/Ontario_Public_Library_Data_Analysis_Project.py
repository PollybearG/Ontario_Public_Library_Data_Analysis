from operator import concat


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datashader.datashape import numeric
from openpyxl.styles.builtins import calculation
from setuptools.extension import Library

df_2017 = pd.read_csv('ontario_public_library_statistics_open_data_july_2019_rev1.csv')
df_2018 = pd.read_csv('ontario_public_library_statistics_open_data_2018.csv')
df_2019 = pd.read_csv('2019_ontario_public_library_statistics_open_data.csv')
df_2020 = pd.read_csv('2020_ontario_public_library_statistics_open_data.csv')

# Combine all the dataset to a new dataset
df_data = pd.concat([df_2017,df_2018,df_2019,df_2020],ignore_index=True, join='outer')

# Replace the blank between words as _ of the column names
df_data.columns = [s.strip().replace(' ', '_') for s in df_data.columns]

print(df_data.columns[:12])

print(df_data.head(5))
print(df_data.tail(5))
print(df_data.shape)
print(df_data.describe())


# Data clean and preparation
# Show the index of the missing values to see know which column has null values
index_missing_values = df_data.isnull().any()
print('The index of missing values in the columns:\n',index_missing_values)

# Show the total missing values in each column
print('The total missing values are \n',df_data.isnull().sum())


# Because there are lots of missing values in the columns and some of them are more than half of the total values in the column
# Removing NaN values will affect the number of samples of data and the accuracy of data analysis
# Instead of removing the missing values, fill in the mean values to the numeric type columns and fill the unknown to the object columns would be better

# Get the numeric data type column
numeric_columns = df_data.select_dtypes(include=['number']).columns
# Get the category and object data type column
category_columns = df_data.select_dtypes(include=['object']).columns

# When writing large numbers, commas are usually used to separate numbers so that the size of the numbers can be seen more clearly,
# but this will change its data type. When performing data analysis, the commas should be deleted and the data type should be restored to the numeric type.
# Look through all the columns that are object but include commas
for col in df_data.columns:
    if df_data[col].dtype == 'object' and df_data[col].str.contains(',').any():
        try:
            df_data[col] = df_data[col].str.replace(',', '').astype(float)
        except ValueError:
            print(f"Column'{col}' contains non-numeric values, can not convert to number type")

# fill in the mean values to the numeric type columns
df_data[numeric_columns] = df_data[numeric_columns].fillna(df_data[numeric_columns].mean())
# fill the unknown to the object columns
df_data[category_columns] = df_data[category_columns].fillna('Unknown')
print('The total missing values are \n',df_data.isnull().sum())


# Count the number of libraries in each city per year
libraryNum_in_city = df_data.groupby(['A1.10_City/Town','Survey_Year_From']).size().unstack()
print(libraryNum_in_city.head(20))


# total number of active cardholders for each library for the last 4 years
Cardholders__each_library_in_city = df_data.groupby(['Library_Full_Name','Survey_Year_From'])['A1.14__No._of_Active_Library_Cardholders'].sum().unstack()
print('The total number of active cardholders for each library for the last 4 years:')
print(Cardholders__each_library_in_city.head(20))


# Find out the top 10 total operate revenues libraries
# Find the average value and sort them from the largest to the last
avg_revenue_per_library = df_data.groupby('Library_Full_Name')['B2.9__Total_Operating_Revenues'].mean()
top_10__revenue_library = avg_revenue_per_library.sort_values(ascending=False).head(10)
print('\nThe Top 10 libraries of operate revenues are:')
print(top_10__revenue_library)

plt.figure(figsize=(10, 6))
top_10__revenue_library.plot(kind='bar', color='skyblue')
plt.title("Top 10 Average Operating Revenues Libraries")
plt.xlabel("Libraries")
plt.ylabel("Average_Operating_Revenue")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# Create a new metric (column) to compare libraries across Ontario (for example, operating revenue per active card holder).

# Calculate the average Revenue per Active CardHolder for each library across all years
# There might be 0 values to be in the Number of Active library Cardholders column, when do the calculation, the result might be infinity. Replace the 0 to NaN value might be more accurate

df_data['A1.14__No._of_Active_Library_Cardholders'] = df_data['A1.14__No._of_Active_Library_Cardholders'].replace(0, np.nan)
df_data['Average_Revenue_Per_CardHolder'] = df_data['B2.9__Total_Operating_Revenues'] / df_data['A1.14__No._of_Active_Library_Cardholders']
avg_cardholder_revenue_per_library = df_data.groupby('Library_Full_Name')['Average_Revenue_Per_CardHolder'].mean()
top_10_ava_carrholder_revenue = avg_cardholder_revenue_per_library.sort_values(ascending=False).head(10)
print('\nThe Top 10 libraries of average cardholder revenues are:')
print(top_10_ava_carrholder_revenue)

plt.figure(figsize=(10, 6))
top_10_ava_carrholder_revenue.plot(kind='bar', color='skyblue')
plt.title("Top 10 Average Cardholder Revenues Libraries")
plt.xlabel("Libraries")
plt.ylabel("Average_Cardholder_Revenue")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Identify key insights around this new metric. These insights should have a theme and build to your
# goal of providing a set of recommendation to your manager on how libraries can be successful.

revenue_relate_columns = ['B2.9__Total_Operating_Revenues',
                          'A1.14__No._of_Active_Library_Cardholders',
                          'G1.5.1.W__No._of_visits_to_the_library_made_in_person','G1.5.2.W__No._of_electronic_visits_to_the_library_website','G1.3.1.W__No._of_people_using_library_workstations',
                          'F2.1.P__No._of_programs_held_annually','F2.2.A__Annual_program_attendance','C0.2.T__Total_Print_Volumes_Held',
                          'Average_Revenue_Per_CardHolder',]

corr_matrix = df_data[revenue_relate_columns].corr()

plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', square=True, linewidths=.5, cbar_kws={"shrink": .5})
plt.title('The correlation of each elements to influence the revenue ')
plt.show()