import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

#connectng DB
connection=sqlite3.connect('database/crime_data.db')
cursor=connection.cursor()
#Retrieving Table Data into DataFrame
df=pd.read_sql('select * from chicago_crime',con=connection)
connection.close()
pd.set_option('display.max_column',None)
pd.set_option('display.max_colwidth',None)
pd.set_option('display.width',1000)
print("\n========= Data Retrieved From Chicago crime Table=========\n")
print(df.head(5))

#Extracting Hours
print(df.info())
df['date']=pd.to_datetime(df['date']) #pd.read_sql makes it at object type so coverting from object type to datetime
# print(df.info())
df['hour']=df['date'].dt.hour
# print(df.head(5))

#calculating No.of Crimes by Hours
crimes_by_hour=df.groupby('hour').size()
print("\n========= Crimes By Hour=========\n")
print(crimes_by_hour)

#plotting crimes per hour of day
plt.figure(figsize=(10,5))
plt.plot(crimes_by_hour.index,crimes_by_hour.values,':bo')
plt.title('Crimes Per Hour Of Day', fontsize=16,fontweight='bold')
plt.xlabel('Hours',fontsize=14,fontweight='bold')
plt.ylabel('Crime Count',fontsize=14,fontweight='bold')
plt.tight_layout()
plt.grid()
plt.savefig('plots/crimes_per_hour.png')
plt.show()

#Computing Mean Crime Per Community Area
connection=sqlite3.connect('database/crime_data.db')
query='''select city.community_name,count(crime.community_code) as crime_count
        from chicago_crime as crime
        left join chicago_city_community as city
        on crime.community_code=city.community_code
        group by city.community_name
        order by crime_count '''
area_crime=pd.read_sql(query,con=connection)
connection.close()
mean_crime=area_crime['crime_count'].mean()
print("\n===== Mean crime count per community area is: =====\n")
print(f'{mean_crime:.2f}')

#box plot to visualy identify outliers
plt.figure(figsize=(8,4))
plt.boxplot(area_crime['crime_count'],orientation='vertical',patch_artist=True, boxprops=dict(facecolor='Green'))
plt.title('Crime Count Community Areas',fontsize=16,fontweight='bold')
plt.ylabel('No.Of Crimes',fontsize=14,fontweight='bold')
plt.tight_layout()
plt.savefig('plots/community_crime_boxplot.png')
plt.show()


# Identifying the  extreme outliers using the IQR method
Q1 = np.percentile(area_crime['crime_count'], 25)
Q3 = np.percentile(area_crime['crime_count'], 75)
IQR = Q3 - Q1
low_bound = Q1 - 1.5 * IQR
up_bound = Q3 + 1.5 * IQR
# print(Q1,Q3,IQR,low_bound,up_bound)

outliers = area_crime[
    (area_crime['crime_count'] < low_bound)
    | (area_crime['crime_count'] > up_bound)
]
print("\n==========The Extreme Outlier Community Areas (High Crime Counts via IQR):==========\n")
print(outliers)

#applying cor() on numeric features
print("\n===== Crime Cross-Correlation Matrix: =====\n")

# Select numeric features
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"Numeric features available: {numeric_cols}")

# Computing correlation matrix using pandas .corr()
corr_matrix = df[numeric_cols].corr()
print(corr_matrix)

# Visualizing correlation matrix using Matplotlib only (plt.imshow)
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, cmap='RdBu', xticklabels=True,yticklabels=True,annot=True, vmin=-1, vmax=1,fmt=".2f",cbar_kws={'label': 'Correlation Coefficient'})
# plt.colorbar(label='Correlation Coefficient')
plt.title('Correlation Matrix of Numeric Features', fontsize=14, fontweight='bold')

plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=65,fontweight='bold')
plt.yticks(range(len(corr_matrix.index)), corr_matrix.index,fontweight='bold')

plt.tight_layout()
plt.savefig('plots/crime_correlation_heatmap.png')
plt.show()