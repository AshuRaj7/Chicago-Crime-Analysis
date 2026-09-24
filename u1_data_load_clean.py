import numpy as np
import pandas as pd
import sqlite3

pd.set_option('display.max_column',None)
pd.set_option('display.width',1000)
pd.set_option('display.unicode.east_asian_width',True)

#Loading the dataset
df= pd.DataFrame(pd.read_csv('datasets/chicago_crime_dataset.csv'))

print("\n=========diaplaying Data and No.Of Rows X Columns=========\n")
print(df.head(10))
print(f'the data consists {df.shape[0]}rows and {df.shape[1]} columns')

print("\n==========Column Data Types & Non-Null Counts==========\n")
print(df.info())

print("\n==========Null-Value Count In Each Column==========\n")
print(df.isnull().sum())
#droping the duplicates
df_clean=df.drop_duplicates().copy()


# Calculating Percentage Of Missing Values in Each Columns
missing_pct = (df_clean.isnull().sum().values / len(df_clean)) * 100
missing_df = pd.DataFrame({'column': df_clean.columns, 'missing_pct': np.round(missing_pct, 2)})
print("\n==========Missing Values Summary (%) Before Handling It==========\n", missing_df[missing_df['missing_pct'] > 0])


#Droping the columns with more than 50% missing values
for col,pct in zip(missing_df['column'], missing_df['missing_pct']):
    if pct > 50:
        df_clean.drop(col, axis=1, inplace=True)

#Updating the values to Handle The Missing Values in Remaining Columns 
df_clean['location_desc'] = df_clean['location_desc'].fillna('Unknown')
df_clean['ward_no'] = df_clean['ward_no'].fillna(df_clean['ward_no'].mode()[0])
df_clean['community_code'] = df_clean['community_code'].fillna(df_clean['community_code'].mode()[0])
df_clean['x_coordinate'] = df_clean['x_coordinate'].fillna(df_clean['x_coordinate'].mode()[0])
df_clean['y_coordinate'] = df_clean['y_coordinate'].fillna(df_clean['y_coordinate'].mode()[0])
df_clean['latitude'] = df_clean['latitude'].fillna(df_clean['latitude'].mode()[0])
df_clean['longitude'] = df_clean['longitude'].fillna(df_clean['longitude'].mode()[0])
df_clean['location'] = df_clean['location'].fillna('Unknown')

#Handling the Data types
df_clean['community_code']=df_clean['community_code'].astype(int)
df_clean['ward_no']=df_clean['ward_no'].astype(int)
print(df_clean.info())

print("\n==========Null-Value Count In Each Column after Handling Missing Values==========\n")
print(df_clean.isnull().sum())


print("\n==========Converting date columns to datetime format==========\n")
df_clean['date'] =pd.to_datetime(df_clean['date'])
df_clean['date_of_update'] =pd.to_datetime(df_clean['date_of_update'])
print("\n==========Data After Handling Missing Values==========\n")
print(df_clean.head())

# 
# df_clean['location']

# List of categorical text columns to clean
categorical_cols = [
    'case_number', 'block', 'iucr_code', 'primary_type', 
    'description', 'location_desc', 'fbi_code'
]

# Strip whitespaces and convert to lowercase across all selected columns
df_clean[categorical_cols] = df_clean[categorical_cols].apply(lambda x: x.astype(str).str.strip().str.lower())
print("\n==========Data After standerdizing Categorical fields==========\n")
print(df_clean.head())

#Extracting Year, Month, Day Of Week from the date column
df_clean['year'] = df_clean['date'].dt.year
df_clean['month'] = df_clean['date'].dt.month
df_clean['day_of_week'] = df_clean['date'].dt.day_of_week


print("\n==========New Features Generated Successfully==========\n")
print(df_clean[['date','year','month','day_of_week']].head(10))

#Count of Unique Crime Types
unique_crime_types_count=df_clean['primary_type'].nunique()
print("\n==========Count of Unique Crime Types==========\n")
print(unique_crime_types_count)


#Inserting Cleaned Data into SQLite Database
connection = sqlite3.connect('database/crime_data.db')
cursor=connection.cursor()
print("\n========== Created Crime Data DataBase Successfully==========\n")
tname='chicago_crime' # this is my table name

# 1. Droping the table if it already exists to recreate it with the correct schema
cursor.execute(f"DROP TABLE IF EXISTS {tname};")

# 2. Creating the table schema 
cursor.execute(f"""
CREATE TABLE {tname} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT,
    block TEXT,
    iucr_code TEXT,
    primary_type TEXT,
    description TEXT,
    location_desc TEXT,
    arrest BOOLEAN,
    domestic BOOLEAN,
    beat TEXT,
    beat_num TEXT,
    district_code TEXT,
    ward_no INTEGER,
    community_code INTEGER,
    fbi_code TEXT,
    x_coordinate REAL,
    y_coordinate REAL,
    year_col INTEGER,
    updated_on TEXT,
    latitude REAL,
    longitude REAL,
    location TEXT,
    date TEXT,
    date_of_update TEXT,
    year INTEGER,
    month INTEGER,
    day_of_week INTEGER
);
""")
connection.commit()
print("\n========== Created Chicago Crime Table successfully==========\n")
df_clean.to_sql(name=tname,con=connection,if_exists='append',index=False)

print("\n========== inserted Data Into the Chicago Crime Table successfully==========\n")
connection.commit()
cursor = connection.cursor()
query="select * from chicago_crime limit 10"
rows = pd.read_sql(query,con=connection)
print("\n========== Data Retrieved from Database Table ==========\n")
print(rows.head(5))

connection.close()



