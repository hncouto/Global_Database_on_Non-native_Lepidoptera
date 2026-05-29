# 1) Required Libraries

import pandas as pd #used to format the data on to the final schema and to work with the dataframes.

# 2) Required Data
ObsData = pd.read_csv(r'../Intermediate Data Tables/RecordsClean.csv', sep=';', encoding="utf-8")
NativeData = pd.read_csv(r"../Intermediate Data Tables/NativeDataClean.csv", sep=";", encoding="utf-8")

# 3) Extract References
References = pd.concat([NativeData[["Reference", "ReferenceYear"]].copy(), ObsData[["Reference", "ReferenceYear"]].copy()]) # Merge the References in the Native and Records dataframes to create a single list of unique references

# 3.1) Update Table
References["Reference Year"] = References["ReferenceYear"].astype(int) # Convert ReferenceYear to integer
References.drop(columns="ReferenceYear", inplace=True) # Drop the ReferenceYear column
References.drop_duplicates(inplace=True) # Drop duplicates keeping a single entry for each Reference

# 3.2) Export References table to check if all references had the same format
References.reset_index(drop=True, inplace=True)
References.to_csv(r"../Intermediate Data Tables/ReferencesExtracted.csv", sep=";", encoding="utf-8", index=False)
