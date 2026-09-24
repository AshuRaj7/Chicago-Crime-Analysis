import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

#connecting to the database and Loading Data from Chicago_crime Table
print("\n=========Connecting to SQLite Database=========\n")
connection = sqlite3.connect('database/crime_data.db')
print("\n=========Connected Successfully=========\n")
cursor = connection.cursor()
q='select * from chicago_crime'
df=pd.read_sql(q,con=connection)
connection.close()
print("\n=========Connection Closed=========\n")

print("\n=========Data Retrieved from Chicago Crime Successfully=========\n")
pd.set_option('display.max_columns',None)
pd.set_option('display.max_colwidth',None)
print(df.head(10))
print(f'\nthe data consists {df.shape[0]}rows and {df.shape[1]} columns\n')

#plotting Total No.Of Crimes Per Year
print("\n=========Ploting Crime Trend Over Years=========\n")
yearly_crimes = df.groupby('year').size()
plt.figure(figsize=(10, 6))
plt.plot(yearly_crimes.index, yearly_crimes.values, '--r*')
plt.grid(True)
plt.title('Total No.Of Crimes Per Year', fontsize=16,fontweight='bold')
plt.xlabel('Year',fontsize=14,fontweight='bold')
plt.ylabel('Total No.Of Crimes',fontsize=14,fontweight='bold')
plt.tight_layout()
plt.savefig('plots/total_crimes_per_year.png')
plt.show()

#Calculating Top 10 Crime Categories
primary_crime=df['primary_type'].value_counts()
top10=primary_crime.sort_values(ascending=False).head(10)
print("\n=========Top 10 Crime Categories=========\n")
print(top10)

#ploting top 10 crime categories
plt.figure(figsize=(10,5))
plt.bar(top10.index,top10.values)
plt.title('Top 10 Crime Categories', fontsize=16,fontweight='bold')
plt.xlabel('Crime Category',fontsize=14,fontweight='bold')
plt.ylabel('No.Of Crimes',fontsize=14,fontweight='bold')
plt.xticks(rotation=65)
plt.tight_layout()
plt.savefig('plots/top10_crime_categories.png')
plt.show()

#Calculating Count and percentage of primary crime categories
primary_crime=primary_crime.reset_index()

primary_crime.columns=['Category','total']

primary_crime['percentage']=(primary_crime[['total']]/len(df))*100
print("\n=========Count and Percentage of Primary Crime Categories=========\n")
print(primary_crime.head(10))

#Calculating percentage Of Crimes Result in Arrest
crime_percent=df['arrest'].sum()/len(df)*100
print(f"\n=========Percentage Of Crimes Result in Arrest=========\n{crime_percent:.2f}%\n")

#Calculating arrest-rate and crime percentage 
arrest_rate=df['arrest'].mean()*100
print(f"\n========= Arrest Rate =========\n{arrest_rate:.2f}%\n")


#Crime frequency pivoted by months vs Day of the week
days = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
df['day_name'] = df['day_of_week'].map(days)
months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
df['month_name'] = df['month'].map(months)

#updating in the db table
connection = sqlite3.connect('database/crime_data.db')
tname='chicago_crime' # this is my table name
df.to_sql(name=tname,con=connection,if_exists='replace',index=False)
connection.commit()
connection.close()

crime_pivot = df.pivot_table(index='month_name', columns='day_name', values='case_number', aggfunc='count', fill_value=0)
print("\n=========Crime Frequency Pivoted by Months vs Day of the Week=========\n")

print(crime_pivot)
highest_crime_month = df.pivot_table(index='month_name', values='case_number', aggfunc='count', fill_value=0).sort_values(by="case_number", ascending=False)
print(highest_crime_month)

#plotting Heatmap of Crime Frequency Pivoted by Months vs Day of the Week

sns.set(style="whitegrid")
plt.figure(figsize=(12, 8))
sns.heatmap(crime_pivot, annot=True, fmt=".2f", cmap="RdBu",linewidths=0.3, cbar_kws={'label': 'Number of Crimes'})
plt.title('Crime Frequency Pivoted by Months vs Day of the Week', fontsize=16,fontweight='bold')
plt.xlabel('Day of the Week',fontsize=14,fontweight='bold')
plt.ylabel('Month',fontsize=14,fontweight='bold')
plt.tight_layout()
plt.savefig('plots/crime_frequency_heatmap.png')
plt.show()

##calculating top 10 community areas names with highest crime count##

#Loading the community city data
print("\n=========City Community Data=========\n")
community_data=pd.read_csv('datasets/chicago_city_community.csv')
print(community_data.head(40))

#checking and handling null values if any
print("\n=========Null-values City Community Data=========\n")
print(community_data.isnull().sum())
community_data.fillna({'community_name':'Unknown'},inplace=True)
#for remaining community_code column dropping the rows with null values
community_data.dropna(subset=['community_code'], inplace=True)

# handling for duplicates if any
community_data.drop_duplicates(inplace=True)

print("\n=========City Community Data after Cleaning=========\n")
print(community_data.head(40))

#connecting to Database
connection = sqlite3.connect('database/crime_data.db')
print("\n=========Connection Established=========\n")
cursor=connection.cursor()
community_data.to_sql(name='chicago_city_community',con=connection,if_exists='replace',index=False)
print("\n========= DataFrame Inserted to Table Chicago_city_community=========\n")
query='select * from chicago_city_community'
rows=pd.read_sql(query,con=connection)
print("\n========= Data Retrieved From City Community Table=========\n")
print(rows)

#joining tables to get the community area names mapped to community code
query='''select crime.community_code,city.community_name,count(crime.community_code) as Countt
        from chicago_crime as crime
        left join chicago_city_community as city
        on crime.community_code=city.community_code
        group by city.community_name
        order by countt desc'''

top10areas=pd.read_sql(query,con=connection)
connection.close()
print("\n=========Top 10 Community Areas with Highest Crime Count=========\n")
print(top10areas.head(10))

#ploting top 10 community areas with highest crime count
plt.figure(figsize=(10,5))
plt.bar(top10areas.head(10)['community_name'],top10areas.head(10)['Countt'])
plt.title('Top 10 Community Areas with Highest Crime Count', fontsize=16,fontweight='bold')
plt.xlabel('Community_Area',fontsize=14,fontweight='bold')
plt.ylabel('No.Of Crimes',fontsize=14,fontweight='bold')
plt.xticks(rotation=65)
plt.tight_layout()
plt.savefig('plots/top10_community_areas.png')
plt.show()


