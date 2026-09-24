import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

#Establishing connection with DB
connection =sqlite3.connect('database/crime_data.db')
cursor=connection.cursor()

crime_query="SELECT id,date,day_of_week,day_name,month,month_name,year,community_code,arrest,primary_type FROM chicago_crime;"
crime_table = pd.read_sql(crime_query,con=connection)
print("\n=========Data Retrieved From Crime table=========\n")
print(crime_table)

#Fetching crime count per year from chicago_crime table
crime_count_per_year=pd.read_sql('select year,count(*) as crimes from chicago_crime group by year order by year asc;',con=connection)
print("\n=========Crime Count Per Year=========\n")
print(crime_count_per_year)

#Fetching Top 5 Crime types and Their Percentages
top5_crime=pd.read_sql('select primary_type,count(*) as crimes, (count(*)/(select count(*) from chicago_crime))*100 as percentage from chicago_crime group by primary_type order by crimes desc limit 5;',con=connection)
print("\n=========Top 5 Crime Categories and Percentage=========\n")
print(top5_crime)

#computing Arrest count per year
arrest_count_year=pd.read_sql('select year,count(arrest) as arrest_count from chicago_crime group by year;',con=connection)
print("\n=========Count Of Arrests Per Year =========\n")
print(arrest_count_year)

#Inserting the summary data into DB as summary tables
crime_count_per_year.to_sql(name='crimes_per_year',con=connection,if_exists='replace',index=False)
top5_crime.to_sql(name='top5_crimes',con=connection,if_exists='replace',index=False)
arrest_count_year.to_sql(name='arrests_per_year',con=connection,if_exists='replace',index=False)
print("\n=========Summary Tables Inserted Into DB Successfully =========\n")


#CREATING VIEWS
#droping views if any exists to avoid views already exists errors upon re-executing
cursor.execute('drop view if exists vw_crime_yearly;')
cursor.execute('drop view if exists vw_crime_by_category;')

#creating vw_crime_yearly view
cursor.execute('''
                create view vw_crime_yearly as
                    select year,count(*) as total_crimes
                    from chicago_crime group by year;
                ''')

#creating vw_crime_by_category
cursor.execute('''
                create view vw_crime_by_category as 
                    select primary_type as category,count(*)  as total_crimes
                    from chicago_crime group by category;
                ''')

connection.commit()
print("\n=========Views Created Successfully =========\n")

#Reading Views Into Pandas DataFrames
crimes_yearly=pd.read_sql('select * from vw_crime_yearly',con=connection)
print("\n========= Fetched From vw_crime_yearly View =========\n")
print(crimes_yearly)
categorical_crimes=pd.read_sql('select * from vw_crime_by_category',con=connection)
print("\n========= Fetched From vw_crime_by_category View =========\n")
print(categorical_crimes)
print("\n=========Data Fetched Successfully From Views=========\n")

#plotting the SQL Fetched Data
plt.figure(figsize=(10,5)) 
plt.bar(crimes_yearly['year'],crimes_yearly['total_crimes'] ,color='darkred')
plt.title('Yearly Crime Count',fontsize=16,fontweight='bold')
plt.xticks(crimes_yearly['year'])
plt.xlabel('Years',fontsize=14,fontweight='bold')
plt.ylabel('Crime Count',fontsize=14,fontweight='bold')
plt.tight_layout()
plt.savefig('plots/crimes_yearly.png')
plt.show()

plt.figure(figsize=(10,5))
plt.bar(categorical_crimes['category'],categorical_crimes['total_crimes'])
plt.title('Total Crimes Per Each Crime-Type',fontsize=16,fontweight='bold')
plt.xlabel('Crime Type',fontsize=14,fontweight='bold')
plt.xticks(rotation=65)
plt.ylabel('Crime Count',fontsize=14,fontweight='bold')
plt.tight_layout()
plt.savefig('plots/crimes_categorically.png')
plt.show()
print("\n=========plotted graphs Successfully From Data Extracted from Views=========\n")