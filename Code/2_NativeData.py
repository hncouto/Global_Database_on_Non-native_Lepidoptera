# 1) Required Libraries

import pandas as pd

# 2) Required Data

# All data was previously manually retrieved and fitted to a predefined schema.
# This data corresponded to the species established recorded in the original data 
# after passing through 1_ObservationData.py

# For the Native data, here on after referred as *NativeData*, it corresponded to:
# - Species: Species name as used on *Observation_TaxonomyClean*.
# - Continent: The corresponding continent of origin of the species regarding the reference used.
# - Realm: The biogeographic realm of origin fitting the updates defined at 10.1126/science.1228282.
# - Reference Year: The year of the reference used to extract the data.
# - Reference: The reference used to extract the data.

NativeData = pd.read_csv(r'../Data Raw/Updated Data/NativeData.csv', sep=';', encoding="utf-8")
Native_mask = pd.read_csv(r'../Intermediate Data Tables/NativeDataExtract.csv', sep=';', encoding="utf-8")

# 3) Data Cleaning

# 3.1) Keep only records for species that have been introduced
NativeData = NativeData[NativeData['Species'].isin(Native_mask['AcceptedSpecies'])]

# 3.2) Remove NA's
NativeData.dropna(subset=['Reference'], inplace=True)

# 4) Exportation

NativeData.reset_index(drop=True, inplace=True)
NativeData.to_csv(r'../Intermediate Data Tables/NativeDataClean.csv', sep =';', encoding='utf-8', index=False)