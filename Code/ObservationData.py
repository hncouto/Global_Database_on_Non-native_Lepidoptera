# 1) Required Libraries

import asyncio #used for the taxonomy updates loops to be done asynchronously and concurrently, saving up time on running the code.
import nest_asyncio #used for the taxonomy updates loops to be done asynchronously and concurrently, saving up time on running the code.
from tenacity import retry, wait_exponential, stop_after_attempt #used to guarantee that the extraction code was not stopped if an error occurred, and if it did occurred to run again for a predefined amount of times with a waiting time between them.
import aiohttp #used to call the different API's, in this case the GBIF Species API, while working with *asyncio* and *nest_asyncio*.
import pandas as pd #used to format the data on to the final schema and to work with the dataframes.

# 2) Required Data

# All data was previously manually retrieved and fitted to a predefined schema.
# For the Observation data, here on after referred as *ObsList*, it corresponded to:
# - Species: Species name used on source, corrected for typos and manually confirmed on Global Names Verifier.
# - NAME_0: The corresponding name of the area that was observed at the predefined regions dataset.
# - Realm: The biogeographic realm of the observation fitting the updates defined at 10.1126/science.1228282.
# - Cryptogenic: A binary variable that corresponded to the cases where the species origin was described as unknown or nativeness uncertain for the observed region. 
# - Dispersal: A binary variable that stated if the species arrived by dispersal either from an introduced region or by natural dispersal from their native range.
# - Eradicated: A binary variable that stated if the species was registered as eradicated to a previous establishment at that region.
# - IntentionalRelease: A binary variable that stated if the species was intentionally released, either for biological control or for any other reason. 
# - Introduced: A binary variable that recorded if the species was considered to have arrived by human action. For the cases that the species dispersed (*Dispersal* = 1) from a region that it was not native to it kept the introduced status (Introduced = 1).
# - Established: A binary variable stating if the species was considered to have a stable population at a certain region independently if it arrived there by dispersal or by man mediated introductions.
# - ReportedFirstYear*: The year of the oldest record according to the source reference.
# - Reference*: The source reference.
# - ReferenceYear*: The year of the source reference, keeping in consideration that a species that was established at a certain point of time can now be eradicated.

ObsList = pd.read_csv(r"../Data Raw/ObsList.csv", sep=";")


# 3) Taxonomy Standardization

# The standardization of the taxonomy was done in 3 main steps: 
# 1. GBIF Standardization: the raw names on ObsList were ran onto the GBIF API in a first instance to standardize according to what were considering as accepted names, keeping the names that were not considered as accepted.
# 2. Global Names Verifier Standardization: to be assure that the most names were captured and that they could be standardized, removing possible false duplicates that were considered as accepted by GBIF as separate species while in fact being one species only, we repeated the process with Global Names Verifier API. 
# 3. GBIF Filtration: After the 2 standardization steps we filtered keeping the accepted name as the one that was found for the standardization on GBIF.

# 3.1) Functions
# 3.1.1) GBIF Names Standardization
nest_asyncio.apply()
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
async def GBIF_Species_1(session, species): 
    url = f"https://api.gbif.org/v1/species/match?name={species}"  
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            if data.get('rank') == 'SPECIES':
                if data.get('status') != 'ACCEPTED':
                    accepted_name = data.get('species') or data.get('canonicalName')
                else:
                    accepted_name = data.get('canonicalName')
                
                return accepted_name if accepted_name else None
            else:
                return species
    except Exception as e:
        print(f"Request failed for species '{species}': {e}")
        return None

async def GBIF_Sessions_1(species_list):
    async with aiohttp.ClientSession() as session:
        tasks = [GBIF_Species_1(session, species) for species in species_list]
        return await asyncio.gather(*tasks)

def GBIF_Extractor_1(species_list):
    return asyncio.get_event_loop().run_until_complete(GBIF_Sessions_1(species_list))

# 3.1.2) GBIF Names Filtration
nest_asyncio.apply()
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
async def GBIF_Species_2(session, species):
    url = f"https://api.gbif.org/v1/species/match?name={species}"  
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            if data.get('rank') == 'SPECIES':
                if data.get('status') != 'ACCEPTED':
                    accepted_name = data.get('species') or data.get('canonicalName')
                else:
                    accepted_name = data.get('canonicalName')
                
                return accepted_name if accepted_name else None
            else:
                return None
    except Exception as e:
        print(f"Request failed for species '{species}': {e}")
        return None

async def GBIF_Sessions_2(species_list):
    async with aiohttp.ClientSession() as session:
        tasks = [GBIF_Species_2(session, species) for species in species_list]
        return await asyncio.gather(*tasks)

def GBIF_Extractor_2(species_list):
    return asyncio.get_event_loop().run_until_complete(GBIF_Sessions_2(species_list))

# 3.1.3) Global Names Verifier Names Cross-Check
nest_asyncio.apply()
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
async def VNF_Species_1(session, species):
    url = f"https://verifier.globalnames.org/api/v1/verifications/{species}?data_sources=1%7C12&all_matches=false&capitalize=false&species_group=false&fuzzy_uninomial=false&stats=true&main_taxon_threshold=0.5"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            if data.get("names", [{}])[0].get("bestResult", {}).get("taxonomicStatus") == 'Accepted':
                accepted_name = data.get("names", [{}])[0].get("bestResult", {}).get('matchedCanonicalSimple')
            else:
                accepted_name = data.get("names", [{}])[0].get("bestResult", {}).get('currentCanonicalSimple')
            return accepted_name if accepted_name != "" else species
            
            
    except Exception as e:
        print(f"Request failed for species '{species}': {e}")
        return None

async def VNF_Sessions_1(species_list):
    async with aiohttp.ClientSession() as session:
        tasks = [VNF_Species_1(session, species) for species in species_list]
        return await asyncio.gather(*tasks)

def VNF_Extractor_1(species_list):
    return asyncio.get_event_loop().run_until_complete(VNF_Sessions_1(species_list))

# 4) Data Cleaning

# Before doing the standardization we kept only the first two words on the *Species* field to keep only the "Genus + Specific Epithet", dropping any possible subspecies that had been recorded and any case that was not identified to the species level.
# We also cleaned encoding and formatting issues (such as *¬†* characters) that could be present based on different file types.

ObsList['Species'] = ObsList['Species'].apply(lambda x: ' '.join(x.split()[:2]))
ObsList = ObsList[~ObsList['Species'].str.contains(r'\bsp\.$', case=False, na=False)]
ObsList = ObsList[~ObsList['Species'].str.contains(r'\bnr\.$', case=False, na=False)]
ObsList['Species'] = (ObsList['Species'].str.normalize('NFKC').str.replace(r'[^\x00-\x7F]+', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip())

ObsList['AcceptedSpecies'] = GBIF_Extractor_2(VNF_Extractor_1(GBIF_Extractor_1(ObsList['Species'])))
ObsList['AcceptedSpecies'] = ObsList['AcceptedSpecies'].apply(lambda x: ' '.join(x.split()[:2]) if isinstance(x, str) else x)

ObsList[ObsList['AcceptedSpecies'].isna()]['Species'].unique()
ObsList[ObsList['AcceptedSpecies'].isna()].shape[0]

# Considering that there were only 23 taxonomy cases, corresponding to only 28 records, that could not be resolved by the applied methodology it was opted to drop these cases. 

ObservationsClean = ObsList.copy()
ObservationsClean.dropna(subset=['AcceptedSpecies'], inplace=True)
ObservationsClean[ObservationsClean['AcceptedSpecies'].isna()]

ObservationsClean.reset_index(drop=True, inplace=True)
ObservationsClean.to_csv(r'../Transformed Data/RecordsClean.csv', sep =';', encoding='utf-8', index=False)

#5) Extraction Taxonomy and References

# 5.1) Required Data
# ObservationsClean = pd.read_csv(r'../Transformed Data/RecordsClean.csv', sep=';', encoding="utf-8")

ObsData = ObservationsClean.copy()

# 5.2) Functions

# 5.2.1) GBIF Family Extractor
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


# 5.2.2) Lepidoptera Cross-Check
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


# 5.3) Extract Taxonomy
TaxonomyData = ObsData[['Species', 'AcceptedSpecies']].copy().drop_duplicates().reset_index(drop=True) # Keep a list of each unique pair of Species and AcceptedSpecies
TaxonomyData = pd.concat([TaxonomyData, 
                          pd.DataFrame({
                              'Species': list(set(TaxonomyData['AcceptedSpecies']) - set(TaxonomyData['Species'])),
                              'AcceptedSpecies': list(set(TaxonomyData['AcceptedSpecies']) - set(TaxonomyData['Species']))})], 
                         ignore_index=True).drop_duplicates().reset_index(drop=True) # At the end of the dataframe for each AcceptedSpecies not in Species, add the AcceptedSpecies as Species and itself as AcceptedSpecies.

# 5.3.1) Automatic Extraction Taxonomy

TaxonomyData['Genus'] = TaxonomyData['AcceptedSpecies'].str.split(' ').str[0] #Keep only the Genus
TaxonomyData['Family'] = GBIF_Family_Extract(TaxonomyData['AcceptedSpecies']) # Extract the Family
TaxonomyData['Lepidoptera'] = GBIF_Lepidoptera_Extract(TaxonomyData['Family'])  # Check if the Family is Lepidoptera

# 5.3.2) Manual Updates
TaxonomyData[(TaxonomyData['Lepidoptera']==0)|(TaxonomyData['Lepidoptera'].isnull())] # Check which families were not identified as Lepidoptera
# Manually correct the unidentified families of the genera to their correct family: Pyralidae and Riodinidae
TaxonomyData.loc[TaxonomyData['Genus'] == 'Homoeographa', 'Family'] = 'Pyralidae' 
TaxonomyData.loc[TaxonomyData['Genus'] == 'Calephelis', 'Family'] = 'Riodinidae'
# As Saturniidae, Pyralidae and Riodinidae are all Lepidopterans and the remaining have been identified as such the cross-check column can be dropped as it is a constant for all.
TaxonomyData.drop(columns=['Lepidoptera'], inplace=True)

# 5.3.3) Export Observation Data Taxonomy Updated
TaxonomyData.to_csv(r'../Transformed Data/Observation_TaxonomyClean.csv', index=False, sep=';', encoding='utf-8')

# 5.4) Extract Data for Native Distribution

Data_NativeExtract = ObsData[['AcceptedSpecies', 'Established']].copy()
Data_NativeExtract = Data_NativeExtract[Data_NativeExtract['Established'] == 1].copy() # Keep only Established Species
Data_NativeExtract = Data_NativeExtract[['AcceptedSpecies']].copy().drop_duplicates().reset_index(drop=True) # Keep a list of each Species

Data_NativeExtract.to_csv(r'../Transformed Data/NativeDataExtract.csv', sep =';', encoding='utf-8', index=False)
