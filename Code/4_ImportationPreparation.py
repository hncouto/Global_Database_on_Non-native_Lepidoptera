# 1) Required Libraries

import pandas as pd #used to format the data on to the final schema and to work with the dataframes.
# 2) Required Data

RecordsData = pd.read_csv(r'../Intermediate Data Tables/RecordsClean.csv', sep=';', encoding="utf-8")
NativeData = pd.read_csv(r"../Intermediate Data Tables/NativeDataClean.csv", sep=";", encoding="utf-8")
References = pd.read_csv(r"../Data Raw/Updated Data/RevisedReferences.csv", sep=";", encoding="utf-8")
Regions = pd.read_csv(r'../Data Raw/RegionsTableData.csv', sep=';', encoding='utf-8')
Realms = pd.read_csv(r'../Data Raw/RealmsTableData.csv', sep=';', encoding='utf-8')
Taxonomy = pd.read_csv(r'../Transformed Data/TaxonomyClean.csv', sep=';', encoding='utf-8')

# 3) Update References

RecordsData_merged = RecordsData.merge(References, on=["Reference", "ReferenceYear"], how="left")
RecordsData_merged['RevisedReference'] = RecordsData_merged['RevisedReference'].fillna(RecordsData_merged['Reference'])
RecordsData_merged['RevisedReferenceYear'] = RecordsData_merged['RevisedReferenceYear'].fillna(RecordsData_merged['ReferenceYear'])
RecordsData_merged.drop(columns=["Reference", "ReferenceYear"], inplace=True)
RecordsData_merged.rename(columns={"RevisedReference": "BibliographicReference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

NativeData_merged = NativeData.merge(References, on=["Reference", "ReferenceYear"], how="left")
NativeData_merged['RevisedReference'] = NativeData_merged['RevisedReference'].fillna(NativeData_merged['Reference'])
NativeData_merged['RevisedReferenceYear'] = NativeData_merged['RevisedReferenceYear'].fillna(NativeData_merged['ReferenceYear'])
NativeData_merged.drop(columns=["Reference", "ReferenceYear"], inplace=True)
NativeData_merged.rename(columns={"RevisedReference": "BibliographicReference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

UpdatedReferences = pd.concat([NativeData_merged[["BibliographicReference", "ReferenceYear"]].copy(), RecordsData_merged[["BibliographicReference", "ReferenceYear"]].copy()]) 
UpdatedReferences = UpdatedReferences[['BibliographicReference', 'ReferenceYear']].drop_duplicates()
UpdatedReferences.reset_index(drop=True, inplace=True)

# 4) Organize Columns and Check names

# 4.1 Records Data
RecordsData_merged = RecordsData_merged[
    ['Species','AcceptedSpecies',
    'NAME_0', 'Realm',
    'Cryptogenic', 'Dispersal', 'Eradicated', 'IntentionalRelease', 'Introduced', 'Established',
    'ReportedFirstYear',
    'BibliographicReference', 'ReferenceYear']].copy()

RecordsData_merged.rename(columns={'ReportedFirstYear': 'Year', 'NAME_0': 'AreaName'}, inplace=True)

# 4.2) Regions Data
Regions = Regions[['AreaID', 'AreaName', 'Country', 'Continent']].copy()

# 5) ID's Creation

# 5.1) References

UpdatedReferences['ReferenceID'] = 'REF' + (UpdatedReferences.index +1).astype(str) 
# Creating the ReferenceID column, which will be used as the primary key for the References table. 
# This code will make the IDs to start with REF1 and complete with the number of rows.


# 5.2) Taxonomy
Taxonomy['SpeciesID'] = 'SP' + (Taxonomy.index +1).astype(str) 
# Creating the SpeciesID column, which will be used as the primary key for the Taxonomy table. 
# This code will make the IDs to start with SP1 and complete with the number of rows.

# 5.3) Realms
Realms['RealmID'] = 'RLM' + (Realms.index +1).astype(str) 
# Creating the RealmID column, which will be used as the primary key for the Realms table. 
# This code will make the IDs to start with RLM1 and complete with the number of rows.


# 6) Link ID's and Keys

# 6.1) Taxonomy

species_to_id = dict(zip(Taxonomy['Species'], Taxonomy['SpeciesID'])) 
# Creating a dictionary with Species as key and SpeciesID 
# as value that will be used to map the SpeciesID column to the AcceptedSpecies column.
Taxonomy['AcceptedSpeciesID'] = Taxonomy['AcceptedSpecies'].map(species_to_id)

Taxonomy_final = Taxonomy[['SpeciesID', 'AcceptedSpeciesID', 
                            'Family', 'Genus', 'Species']].copy()

# 6.2) Records

# 6.2.1) AreaID
RecordsData_Updated = RecordsData_merged.merge(Regions, left_on='AreaName', right_on='AreaName', how='left') 
# Merge with the Regions dataframe to attribute the respective AreaID
RecordsData_Updated.drop(columns=['Country', 'Continent'], inplace=True) 
# Drop the AreaName column and respective information keeping only the AreaID

# 6.2.2) RealmID
RecordsData_Updated = RecordsData_Updated.merge(Realms, left_on='Realm', right_on='Realm', how='left') 
# Merge with the Realms dataframe to attribute the respective RealmID


# 6.2.3) ReferenceID
RecordsData_Updated = RecordsData_Updated.merge(UpdatedReferences, left_on='BibliographicReference', right_on='BibliographicReference', how='left') 
# Merge with the UpdatedReferences dataframe to attribute the respective ReferenceID
RecordsData_Updated.drop(columns=['ReferenceYear_x', 'ReferenceYear_y'], inplace=True) 
# Drop the BibliographicReference column and respective information keeping only the ReferenceID

# 6.2.4) SpeciesID
RecordsData_Updated = RecordsData_Updated.merge(Taxonomy, left_on='Species', right_on='Species', how='left') 
# Merge with the Taxonomy dataframe to attribute the respective SpeciesID
RecordsData_Updated.drop(columns=['AcceptedSpeciesID', 'AcceptedSpecies_x', 'AcceptedSpecies_y','Family', 'Genus'], inplace=True) 
# Drop the AcceptedSpecies column and respective information keeping only the SpeciesID

# 6.2.5) Create RecordsID 

RecordsData_Updated.reset_index(drop=True, inplace=True)
RecordsData_Updated['RecordID'] = 'REC' + (RecordsData_Updated.index +1).astype(str) 
# Creating the RecordID column, which will be used as the primary key for the Observations table. 
# This code will make the IDs to start with REC1 and complete with the number of rows. 
 

# 6.2.6) Reorder Columns
RecordsData_Updated = RecordsData_Updated[[
    'RecordID',
    'SpeciesID', 'Species',
    'AreaID', 'AreaName',
    'RealmID', 'Realm',
    'Cryptogenic', 'IntentionalRelease', 'Introduced', 'Dispersal', 'Established', 'Eradicated', 'Year', 
    'ReferenceID', 'BibliographicReference']].copy()

# 6.2.7) Cleaned Columns
RecordsData_Final = RecordsData_Updated[[
    'RecordID',
    'SpeciesID',
    'AreaID',
    'RealmID',
    'Cryptogenic', 'IntentionalRelease', 'Introduced', 'Dispersal', 'Established', 'Eradicated', 'Year', 
    'ReferenceID']].copy()

# 6.3) References

References_Final = UpdatedReferences[['ReferenceID', 'BibliographicReference', 'ReferenceYear']]
References_Final["BibliographicReference"] = '"' + References_Final["BibliographicReference"].astype(str) + '"'
References_Final["BibliographicReference"] = References_Final["BibliographicReference"].str.replace(",", "", regex=False)

# 6.4) Natives
Natives_DB = NativeData[['Species', 'Continent', 'Realm', 'Reference']].copy() 
#Create a copy of the dataframe, organized and with the relevant columns, avoiding to repeat information
Natives_DB.rename(columns={'Reference': 'BibliographicReference'}, inplace=True) 
#Rename the column for merging and better readability

# 6.4.1) Realms
Natives_DB = Natives_DB.merge(Realms, on='Realm', how='left') #Merge with the Realms dataframe to attribute the respective RealmID
Natives_DB.drop(columns='Realm', inplace=True) #Drop the Realm column keeping the RealmID

# 6.4.2) Taxonomy
Natives_DB = Natives_DB.merge(Taxonomy_final, on='Species', how='left')
#Merge with the Taxonomy dataframe to attribute the respective SpeciesID
Natives_DB.drop(columns=['Species', 'Genus', 'Family', 'AcceptedSpeciesID'], inplace=True)
#Drop the Species column and respective information keeping only the SpeciesID

# 6.4.3) References
Natives_DB = Natives_DB.merge(UpdatedReferences, on='BibliographicReference', how='left')
#Merge with the UpdatedReferences dataframe to attribute the respective ReferenceID
Natives_DB.drop(columns=['BibliographicReference', 'ReferenceYear'], inplace=True)
#Drop the BibliographicReference column and respective information keeping only the ReferenceID

# 6.4.4) Reorder Columns
Natives_DB = Natives_DB[['SpeciesID', 'Continent', 'RealmID', 'ReferenceID']]

# 7) Exportation

# 7.1) Clean Tables
NativeData_merged.to_csv(r'../Transformed Data/NativesClean.csv', sep=';', index=False)
RecordsData_Updated.to_csv(r'../Transformed Data/RecordsClean.csv', sep=';', index=False)
UpdatedReferences.to_csv(r'../Transformed Data/ReferencesClean.csv', sep=';', index=False)
Regions.to_csv(r'../Transformed Data/RegionsClean.csv', sep=';', index=False)
Realms.to_csv(r'../Transformed Data/RealmsClean.csv', sep=';', index=False)

# 7.2) Database Tables
Taxonomy_final.to_csv(r'../Database Tables/Base_Taxonomy.csv', sep=',', index=False)
RecordsData_Final.to_csv(r'../Database Tables/Obs_Records_DB.csv', sep=',', index=False)
Regions.to_csv(r'../Database Tables/Geography_Regions.csv', sep=',', index=False)
Realms.to_csv(r'../Database Tables/Geography_Realms.csv', sep=',', index=False)
References_Final.to_csv(r'../Database Tables/Base_References.csv', sep=',', index=False)
Natives_DB.to_csv(r'../Database Tables/Obs_NativesDB.csv', sep=',', index=False)