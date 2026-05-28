# 1) Required Libraries

import asyncio #used for the taxonomy updates loops to be done asynchronously and concurrently, saving up time on running the code.
import nest_asyncio #used for the taxonomy updates loops to be done asynchronously and concurrently, saving up time on running the code.
from tenacity import retry, wait_exponential, stop_after_attempt #used to guarantee that the extraction code was not stopped if an error occurred, and if it did occurred to run again for a predefined amount of times with a waiting time between them.
import aiohttp #used to call the different API's, in this case the GBIF Species API, while working with *asyncio* and *nest_asyncio*.
import pandas as pd #used to format the data on to the final schema and to work with the dataframes.

# 2) Required Data
ObsData = pd.read_csv(r'../Transformed Data/RecordsClean.csv', sep=';', encoding="utf-8")
NativeData = pd.read_csv(r"../Transformed Data/NativeDataClean.csv", sep=";", encoding="utf-8")

# 3) Extract References
References = pd.concat([NativeData[["Reference", "ReferenceYear"]].copy(), ObsData[["Reference", "ReferenceYear"]].copy()]) # Merge the References in the Native and Records dataframes to create a single list of unique references

# 3.1) Update Table
References["Reference Year"] = References["ReferenceYear"].astype(int) # Convert ReferenceYear to integer
References.drop(columns="ReferenceYear", inplace=True) # Drop the ReferenceYear column
References.drop_duplicates(inplace=True) # Drop duplicates keeping a single entry for each Reference

# 3.2) Export References table to check if all references had the same format
References.reset_index(drop=True, inplace=True)
References.to_csv(r"../Transformed Data/ReferencesExtracted.csv", sep=";", encoding="utf-8", index=False)

# 3.3) Re-import references to update them
#References = pd.read_csv(r"../Raw Data/ReferencesExtracted.csv", sep=";", encoding="utf-8")

