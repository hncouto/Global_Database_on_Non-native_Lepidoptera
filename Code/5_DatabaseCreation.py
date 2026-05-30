# 1) Required Libraries

import pandas as pd
import sqlite3
import os

# 2) Required Data

TaxonomyData = pd.read_csv(r"../Database Tables/Base_Taxonomy.csv", sep=",", encoding="utf-8")

# 3) SQLite Database Creation

# 3.1) Create Connection
con = sqlite3.connect("../Database/WDNnL.db") 
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

cur.execute("""DROP TABLE Taxonomy""") 
# SQL code to drop the Taxonomy table, kept for testing purposes