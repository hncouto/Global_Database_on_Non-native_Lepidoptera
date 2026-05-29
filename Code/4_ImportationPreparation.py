# 1) Required Libraries

import pandas as pd #used to format the data on to the final schema and to work with the dataframes.

# 2) Required Data

ObsData = pd.read_csv(r'../Intermediate Data Tables/RecordsClean.csv', sep=';', encoding="utf-8")
NativeData = pd.read_csv(r"../Intermediate Data Tables/NativeDataClean.csv", sep=";", encoding="utf-8")
References = pd.read_csv(r"../Data Raw/Updated Data/RevisedRaferences.csv", sep=";", encoding="utf-8")
Regions = pd.read_csv(r'../Data Raw/RegionsTableData.csv', sep=';', encoding='utf-8')
#Realms = pd.read_csv(r'../Data Raw/RealmsTableData.csv', sep=';', encoding='utf-8')
Taxonomy = pd.read_csv(r'../Transformed Data/TaxonomyClean.csv', sep=';', encoding='utf-8')

# 3) Update References

ObsData_merged = ObsData.merge(References, on=["Reference", "ReferenceYear"], how="left")
ObsData_merged.drop(columns=["Reference", "ReferenceYear"], inplace=True)
ObsData_merged.rename(columns={"RevisedReference": "BibliographicReference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

NativeData_merged = NativeData.merge(References, on=["Reference", "ReferenceYear"], how="left")
NativeData_merged.drop(columns=["Reference", "ReferenceYear"], inplace=True)
NativeData_merged.rename(columns={"RevisedReference": "BibliographicReference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

UpdatedReferences = References[['RevisedReference', 'RevisedReferenceYear']].drop_duplicates()
UpdatedReferences.reset_index(drop=True, inplace=True)
UpdatedReferences.rename(columns={"RevisedReference": "BibliographicReference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

# 4) Organize Columns and Check names

# 4.1 Observation Data
ObsData_merged = ObsData_merged[
    ['Species','AcceptedSpecies',
    'NAME_0', 'Realm',
    'Cryptogenic', 'Dispersal', 'Eradicated', 'IntentionalRelease', 'Introduced', 'Established',
    'ReportedFirstYear',
    'BibliographicReference', 'ReferenceYear']].copy()

ObsData_merged.rename(columns={'ReportedFirstYear': 'Year', 'NAME_0': 'AreaName'}, inplace=True)

# 4.2) Regions Data
Regions = Regions[['AreaID', 'AreaName', 'Country', 'Continent']].copy()

# 5) ID's Creation

# 5.1) References

References['ReferenceID'] = 'REF' + (References.index +1).astype(str) 
# Creating the ReferenceID column, which will be used as the primary key for the References table. 
# This code will make the IDs to start with REF1 and complete with the number of rows.


# 5.2) Taxonomy
Taxonomy['SpeciesID'] = 'SP' + (Taxonomy.index +1).astype(str) 
# Creating the SpeciesID column, which will be used as the primary key for the Taxonomy table. 
# This code will make the IDs to start with SP1 and complete with the number of rows.


# 5.3) Observations

ObsData_final.reset_index(drop=True, inplace=True)

Records_DB['RecordID'] = 'REC' + (Records_DB.index +1).astype(str) 

# 6) Link ID's and Keys

# 6.1) Taxonomy

species_to_id = dict(zip(Taxonomy['Species'], Taxonomy['SpeciesID'])) 
# Creating a dictionary with Species as key and SpeciesID 
# as value that will be used to map the SpeciesID column to the AcceptedSpecies column.
Taxonomy['AcceptedSpeciesID'] = Taxonomy['AcceptedSpecies'].map(species_to_id)

Taxonomy_final = Taxonomy[['SpeciesID', 'AcceptedSpeciesID', 
                            'Family', 'Genus', 'Species']].copy()

# 7) Exportation
NativeData_merged.to_csv(r'../Transformed Data/NativesClean.csv', sep=';', index=False)
ObsData_merged.to_csv(r'../Transformed Data/ObservationsClean.csv', sep=';', index=False)
UpdatedReferences.to_csv(r'../Transformed Data/ReferencesClean.csv', sep=';', index=False)
Regions.to_csv(r'../Transformed Data/RegionsClean.csv', sep=';', index=False)

Taxonomy_final.to_csv(r'../Database Tables/Base_Taxonomy.csv', sep=';', index=False)
