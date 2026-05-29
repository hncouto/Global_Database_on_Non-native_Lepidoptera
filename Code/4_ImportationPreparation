# 1) Required Libraries

import pandas as pd #used to format the data on to the final schema and to work with the dataframes.

# 2) Required Data

ObsData = pd.read_csv(r'../Transformed Data/RecordsClean.csv', sep=';', encoding="utf-8")
NativeData = pd.read_csv(r"../Transformed Data/NativeDataClean.csv", sep=";", encoding="utf-8")
References = pd.read_csv(r"../Data Raw/Updated Data/RevisedRaferences.csv", sep=";", encoding="utf-8")

# 3) Update References

ObsData_merged = ObsData.merge(References, on=["Reference", "ReferenceYear"], how="left")
ObsData_merged.drop(columns=["Reference", "ReferenceYear"], inplace=True)
ObsData_merged.rename(columns={"RevisedReference": "Reference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

NativeData_merged = NativeData.merge(References, on=["Reference", "ReferenceYear"], how="left")
NativeData_merged.drop(columns=["Reference", "ReferenceYear"], inplace=True)
NativeData_merged.rename(columns={"RevisedReference": "Reference", "RevisedReferenceYear": "ReferenceYear"}, inplace=True)

# 4) Organize Columns and Check names

# 5) ID's Creation

# 6) Exportation

# 7) Exportation

