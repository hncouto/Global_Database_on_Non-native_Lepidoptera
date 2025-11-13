# 1) Required Libraries

import asyncio #used for the taxonomy updates loops to be done asynchronously and concurrently, saving up time on running the code.
import nest_asyncio #used for the taxonomy updates loops to be done asynchronously and concurrently, saving up time on running the code.
from tenacity import retry, wait_exponential, stop_after_attempt #used to guarantee that the extraction code was not stopped if an error occurred, and if it did occurred to run again for a predefined amount of times with a waiting time between them.
import aiohttp #used to call the different API's, in this case the GBIF Species API, while working with *asyncio* and *nest_asyncio*.
import pandas as pd #used to format the data on to the final schema and to work with the dataframes.

# 2) Required Data
ObsData = pd.read_csv(r'../Transformed Data/RecordsClean.csv', sep=';', encoding="utf-8")
NativeData = pd.read_csv(r"../Transformed Data/NativeDataClean.csv", sep=";", encoding="utf-8")

# 3) Functions

# 3.1) GBIF Family Extractor
nest_asyncio.apply()
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5)) #used to guarantee that the extraction code was not stopped if an error occurred, and if it did occurred to run again for a predefined amount of times with a waiting time between them.
async def GBIF_Family_List(session, species):
    '''
    List Retainer: Extracts the family of a species from the GBIF Species API.
    
    Args:
        session: aiohttp.ClientSession object. 
        species: str. corresponding to the species name.
        
    Returns:
        str.
    '''
    url = f"https://api.gbif.org/v1/species/match?name={species}" #GBIF Species API for the species listed
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            if data.get('family'):
                return data.get('family')
            else:
                return None
    
    except Exception as e:
        print(f"Request failed for species '{species}': {e}")
        return None

async def GBIF_Family_Sessions(species_list):
    '''
    Session Creator: Takes a list of species and for each species in the list it creates a session to be called in the future.
    
    Args:
        species_list: list. list of species names.
        
    Returns:
        sessions list for each species listed.
    '''
    async with aiohttp.ClientSession() as session:
        tasks = [GBIF_Family_List(session, species) for species in species_list]
        return await asyncio.gather(*tasks)

def GBIF_Family_Extract(species_list):
    '''The Extractor: It calls the Session Creator, running the list of tasks returning the results for each genera in the list using the function on the List Retainer.
    
    Args:
        species_list: list. list of species names.
        
    Returns:
        Family list corresponding to the species listed.
    '''
    return asyncio.get_event_loop().run_until_complete(GBIF_Family_Sessions(species_list))


# 3.2) Lepidoptera Cross-Check
nest_asyncio.apply()
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5)) #used to guarantee that the extraction code was not stopped if an error occurred, and if it did occurred to run again for a predefined amount of times with a waiting time between them.
async def GBIF_Lepidoptera_List(session, family):
    
    url = f"https://api.gbif.org/v1/species/match?name={family}" #GBIF Species API for the family listed
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            if data.get('order') == 'Lepidoptera':
                return 1
            elif data.get('order') is None:
                return None
            else:
                return 0
            
    except Exception as e:
        print(f"Error fetching data for {family}: {e}")
        return False

async def GBIF_Lepidoptera_Sessions(family_list):
    async with aiohttp.ClientSession() as session:
        tasks = [GBIF_Lepidoptera_List(session, family) for family in family_list]
        return await asyncio.gather(*tasks)

def GBIF_Lepidoptera_Extract(family_list):
    '''The Extractor: It calls the Session Creator, running the list of tasks returning the results for each family in the list using the function on the List Retainer.
    
    Given a list of families checks if they are listed as Lepidoptera or not under the GBIF Species API.
    
    Args:
        family_list: list. list of families names.
        
    Returns:
        1 or 0 depending if the family is listed as Lepidoptera or not for the GBIF Species API.
    '''
    return asyncio.get_event_loop().run_until_complete(GBIF_Lepidoptera_Sessions(family_list))


# 4) Extract Taxonomy
TaxonomyData = ObsData[['Species', 'AcceptedSpecies']].copy().drop_duplicates().reset_index(drop=True) # Keep a list of each unique pair of Species and AcceptedSpecies
TaxonomyData = pd.concat([TaxonomyData, 
                          pd.DataFrame({
                              'Species': list(set(TaxonomyData['AcceptedSpecies']) - set(TaxonomyData['Species'])),
                              'AcceptedSpecies': list(set(TaxonomyData['AcceptedSpecies']) - set(TaxonomyData['Species']))})], 
                         ignore_index=True).drop_duplicates().reset_index(drop=True) # At the end of the dataframe for each AcceptedSpecies not in Species, add the AcceptedSpecies as Species and itself as AcceptedSpecies.

# 4.1) Automatic Extraction Taxonomy

TaxonomyData['Genus'] = TaxonomyData['AcceptedSpecies'].str.split(' ').str[0] #Keep only the Genus
TaxonomyData['Family'] = GBIF_Family_Extract(TaxonomyData['AcceptedSpecies']) # Extract the Family
TaxonomyData['Lepidoptera'] = GBIF_Lepidoptera_Extract(TaxonomyData['Family'])  # Check if the Family is Lepidoptera

# 4.2) Manual Updates
TaxonomyData[(TaxonomyData['Lepidoptera']==0)|(TaxonomyData['Lepidoptera'].isnull())] # Check which families were not identified as Lepidoptera
# Manually correct the unidentified families of the genera to their correct family: Pyralidae and Riodinidae
TaxonomyData.loc[TaxonomyData['Genus'] == 'Homoeographa', 'Family'] = 'Pyralidae' 
TaxonomyData.loc[TaxonomyData['Genus'] == 'Calephelis', 'Family'] = 'Riodinidae'
# As Saturniidae, Pyralidae and Riodinidae are all Lepidopterans and the remaining have been identified as such the cross-check column can be dropped as it is a constant for all.
TaxonomyData.drop(columns=['Lepidoptera'], inplace=True)

# 4.3) Export Taxonomy table to import into the database
TaxonomyData.to_csv(r'../Transformed Data/TaxonomyClean.csv', index=False, sep=';', encoding='utf-8')


# 5) Extract References
References = pd.concat([NativeData[["Reference", "ReferenceYear"]].copy(), ObsData[["Reference", "ReferenceYear"]].copy()]) # Merge the References in the Native and Records dataframes to create a single list of unique references

# 5.1) Update Table
References["Reference Year"] = References["ReferenceYear"].astype(int) # Convert ReferenceYear to integer
References.drop(columns="ReferenceYear", inplace=True) # Drop the ReferenceYear column
References.drop_duplicates(inplace=True) # Drop duplicates keeping a single entry for each Reference

# 5.2) Export References table to import into the database
References.reset_index(drop=True, inplace=True)
References.to_csv(r"../Transformed Data/ReferencesClean.csv", sep=";", encoding="utf-8", index=False)

