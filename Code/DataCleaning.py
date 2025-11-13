# 1) Required Libraries
import asyncio
import nest_asyncio
from tenacity import retry, wait_exponential, stop_after_attempt
import aiohttp
import pandas as pd

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
NativeData = pd.read_csv(r"../Data Raw/NativeData.csv", sep=";")

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
