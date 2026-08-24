# 1) Required Libraries

import pandas as pd
import sqlite3
import os

# 2) Required Data

TaxonomyData = pd.read_csv(r"../Database Tables/Base_Taxonomy.csv", sep=",", encoding="utf-8")
RegionsData = pd.read_csv(r"../Database Tables/Geography_Regions.csv", sep=",", encoding="utf-8")
RealmsData = pd.read_csv(r"../Database Tables/Geography_Realms.csv", sep=",", encoding="utf-8")
ReferencesData = pd.read_csv(r"../Database Tables/Base_References.csv", sep=",", encoding="utf-8")
NativeDistData = pd.read_csv(r"../Database Tables/Obs_NativesDB.csv", sep=",", encoding="utf-8")
RecordsData = pd.read_csv(r"../Database Tables/Obs_Records_DB.csv", sep=",", encoding="utf-8")

# 3) SQLite Database Creation

# 3.1) Create Connection
con = sqlite3.connect("../Database/GNOLEP.db") 
# Create a connector to the database file or a file if it doesn't exist
con.execute("PRAGMA foreign_keys = ON") 
# Enable foreign keys in the new database
cur = con.cursor() 
# Create a cursor to execute SQL commands
tables_check = cur.execute("SELECT name FROM sqlite_master") 
# SQL code to check the existing tables in the database
tables_check.fetchall() 
# Execute the SQL code

# 3.2) Create Taxonomy Table
TaxonomyData = TaxonomyData.reset_index(drop=True) 
# Reset the index of the Taxonomy dataframe

cur.execute("""CREATE TABLE IF NOT EXISTS Taxonomy (
    SpeciesID VARCHAR(7) PRIMARY KEY, 
    AcceptedSpeciesID VARCHAR(7),
    Species TEXT, 
    Genus TEXT, 
    Family TEXT,
    FOREIGN KEY (AcceptedSpeciesID) REFERENCES Taxonomy(SpeciesID) ON DELETE SET NULL)
    """)
#SQL code to create the Taxonomy table, using the SpeciesID as the primary key and the AcceptedSpeciesID as a foreign key.
#The types of each column are also defined as VARCHAR(7) for SpeciesID and AcceptedSpeciesID and TEXT for the remaining columns

cols = ['SpeciesID', 'AcceptedSpeciesID', 'Species', 'Genus', 'Family'] 
# Define the columns to be selected and inserted into the database

BaseTaxonomy = TaxonomyData[TaxonomyData['SpeciesID'] == TaxonomyData['AcceptedSpeciesID']] 
# Select only the rows where the SpeciesID is equal to the AcceptedSpeciesID
BaseTaxonomy = BaseTaxonomy[cols] 
# Select only the columns defined in the cols variable
BaseTaxonomy.to_sql('Taxonomy', con, if_exists='append', index=False) 
# Insert the selected rows into the Taxonomy table in the database
con.commit() 
# Commit the changes

ComposedTaxonomy = TaxonomyData[TaxonomyData['SpeciesID'] != TaxonomyData['AcceptedSpeciesID']] 
# Select only the rows where the SpeciesID is not equal to the AcceptedSpeciesID
ComposedTaxonomy = ComposedTaxonomy[cols] 
# Select only the columns defined in the cols variable
ComposedTaxonomy.to_sql('Taxonomy', con, if_exists='append', index=False) 
# Insert the selected rows into the Taxonomy table in the database
con.commit() 
# Commit the changes

Taxonomy_check = cur.execute("SELECT * FROM Taxonomy") 
# SQL code to select all the rows from the Taxonomy table

Taxonomy_check.fetchone() 
# Execute the SQL code, fetching only the results for the first row

# cur.execute("""DROP TABLE Taxonomy""") 
# SQL code to drop the Taxonomy table, kept for testing purposes


# 3.3) Create Regions Table
RegionsData = RegionsData[['AreaID', 'AreaName', 'Country', 'Continent']] 
# Select only the columns to be inserted into the database
RegionsData = RegionsData.reset_index(drop=True) 
# Reset the index of the Regions dataframe

cur.execute("""CREATE TABLE IF NOT EXISTS Regions (
    AreaID VARCHAR(8) PRIMARY KEY, 
    AreaName TEXT, 
    Country TEXT, 
    Continent TEXT)
    """)
# SQL code to create the Regions table, using the AreaID as the primary key
# The types of each column are also defined as VARCHAR(8) for AreaID and TEXT for the remaining columns

RegionsData.to_sql('Regions', con, if_exists='append', index=False) 
# Insert the Regions data into the Regions table in the database

con.commit() 
# Commit the changes

Regions_check = cur.execute('SELECT * FROM "Regions"') 
# SQL code to select all the rows from the Regions table

Regions_check.fetchone() 
# Execute the previous SQL code, fetching only the results for the first row

#cur.execute("""DROP TABLE Regions""") 
# SQL code to drop the Regions table, kept for testing purposes


# 3.4) Create Realms Table
RealmsData = RealmsData[['RealmID', 'Realm']] 
# Reorder and select the columns to be inserted into the database
RealmsData = RealmsData.reset_index(drop=True) 
# Reset the index of the Realms dataframe

cur.execute("""CREATE TABLE IF NOT EXISTS Realms (
    RealmID VARCHAR(5) PRIMARY KEY, 
    Realm TEXT)
    """)
# SQL code to create the Realms table, using the RealmID as the primary key
# The types of each column are also defined as VARCHAR(5) for RealmID and TEXT for the Realm column

RealmsData.to_sql('Realms', con, if_exists='append', index=False) 
# Insert the Realms data into the Realms table in the database

con.commit() 
# Commit the changes

Realms_check = cur.execute('SELECT * FROM "Realms"') 
# SQL code to select all the rows from the Realms table

Realms_check.fetchone() 
# Execute the previous SQL code, fetching only the results for the first row

#cur.execute("""DROP TABLE Realms""") 
# SQL code to drop the Realms table, kept for testing purposes

# 3.5) References
ReferencesData = ReferencesData.reset_index(drop=True) 
# Reset the index of the References dataframe

cur.execute("""CREATE TABLE IF NOT EXISTS "References" (
    ReferenceID VARCHAR(7) PRIMARY KEY, 
    BibliographicReference TEXT, 
    ReferenceYear INTEGER
)""")
# SQL code to create the References table, using the ReferenceID as the primary key
# The types of each column are also defined as VARCHAR(7) for ReferenceID, TEXT for BibliographicReference and INTEGER for ReferenceYear

ReferencesData.to_sql('References', con, if_exists='append', index=False) 
# Insert the References data into the References table in the database
con.commit() 
# Commit the changes

References_check = cur.execute('SELECT * FROM "References"') 
# SQL code to select all the rows from the References table
References_check.fetchone() 
# Execute the previous SQL code, fetching only the results for the first row

#cur.execute('DROP TABLE "References"') 
# SQL code to drop the References table, kept for testing purposes

# 3.6) Native Distribution
NativeDistData = NativeDistData.reset_index(drop=True) 
# Reset the index of the Natives dataframe

cur.execute("""
CREATE TABLE IF NOT EXISTS NativeDistribution (
    SpeciesID VARCHAR(7), 
    RealmID VARCHAR(5), 
    Continent TEXT,
    ReferenceID VARCHAR(7), 
    FOREIGN KEY (SpeciesID) REFERENCES Taxonomy(SpeciesID) ON DELETE SET NULL,
    FOREIGN KEY (RealmID) REFERENCES Realms(RealmID) ON DELETE SET NULL,
    FOREIGN KEY (ReferenceID) REFERENCES "References"(ReferenceID) ON DELETE SET NULL
)""")

# SQL code to create the NativeDistribution table, using the SpeciesID as the primary key and the RealmID and ReferenceID as foreign keys referring to the respective tables
# The types of each column are also defined as VARCHAR(7) for SpeciesID and ReferenceID, VARCHAR(5) for RealmID, TEXT for Continent and INTEGER for Cosmopolitan
# In case the ReferenceID column does not exist in the References table, the value will be set to NULL
# In case the RealmID column does not exist in the Realms table, the value will be set to NULL
# In case the SpeciesID column does not exist in the Taxonomy table, the value will be set to NULL 

NativeDistData.to_sql('NativeDistribution', con, if_exists='append', index=False) 
# Insert the Natives data into the NativeDistribution table in the database
con.commit() 
# Commit the changes

NativeDist_check = cur.execute('SELECT * FROM NativeDistribution') 
# SQL code to select all the rows from the NativeDistribution table
NativeDist_check.fetchone() 
# Execute the previous SQL code, fetching only the results for the first row

#cur.execute('DROP TABLE NativeDistribution') 
# SQL code to drop the NativeDistribution table, kept for testing purposes

# 3.7) Records

RecordsData = RecordsData.reset_index(drop=True) 
# Reset the index of the Records dataframe

cur.execute("""
CREATE TABLE IF NOT EXISTS Records (
    RecordID VARCHAR(9) PRIMARY KEY,
    SpeciesID VARCHAR(7),
    AreaID VARCHAR(8), 
    RealmID VARCHAR(5), 
    Cryptogenic INTEGER CHECK (Cryptogenic IN (0, 1) OR Cryptogenic IS NULL),
    IntentionalRelease INTEGER CHECK (Cryptogenic IN (0, 1) OR Cryptogenic IS NULL),
    Introduced INTEGER CHECK (Introduced IN (0, 1) OR Introduced IS NULL),
    Dispersal INTEGER CHECK (Dispersal IN (0, 1) OR Dispersal IS NULL),
    Established INTEGER CHECK (Established IN (0, 1) OR Established IS NULL),
    Eradicated INTEGER CHECK (Eradicated IN (0, 1) OR Eradicated IS NULL),
    Year INTEGER,
    ReferenceID VARCHAR(7),
    FOREIGN KEY (SpeciesID) REFERENCES Taxonomy(SpeciesID) ON DELETE SET NULL,
    FOREIGN KEY (AreaID) REFERENCES Regions(AreaID) ON DELETE SET NULL,
    FOREIGN KEY (RealmID) REFERENCES Realms(RealmID) ON DELETE SET NULL,
    FOREIGN KEY (ReferenceID) REFERENCES "References"(ReferenceID) ON DELETE SET NULL
)""")

# SQL code to create the Records table, using the SpeciesID as the primary key and the AreaID, RealmID and ReferenceID as foreign keys referring to the respective tables
# The types of each column are also defined as VARCHAR(7) for SpeciesID and ReferenceID, VARCHAR(8) for AreaID, VARCHAR(5) for RealmID, INTEGER for all other columns
# In case a column that has a foreign key does not exist in the respective table, the value will be set to NULL
# In case a non Year column that is an integer has a value other than 0 or 1, the value will be set to NULL

RecordsData.to_sql('Records', con, if_exists='append', index=False) 
# Insert the Records data into the Records table in the database
con.commit() 
# Commit the changes

Records_check = cur.execute('SELECT * FROM Records') 
# SQL code to select all the rows from the Records table
Records_check.fetchone() 
# Execute the previous SQL code, fetching only the results for the first row

#cur.execute('DROP TABLE Records') 
# SQL code to drop the Records table, kept for testing purposes

# 4) Close Connector
con.close() 
#Close the connection to the database

# 5) Export Database
os.rename(r'../Database/GNOLEP.db', r'../Database/GNOLEP.sqlite') 
#Rename the GNOLEP.db file to GNOLEP.sqlite for better readability

con = sqlite3.connect("../Database/GNOLEP.sqlite") 
#Connect to the GNOLEP.sqlite database
cur = con.cursor() 
#Create a cursor to execute SQL commands

tables_check = cur.execute("SELECT name FROM sqlite_master") 
#SQL code to select all the tables from the database
tables_check.fetchall() 
#Execute the SQL code

con.close() 
#Close the connection to the database