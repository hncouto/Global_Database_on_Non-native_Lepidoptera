# Global Database on Non-native Lepidoptera (GNOLEP) 

Repository for the code, development and data of the **Global Database on Non-native Lepidoptera (GNOLEP)**. 


## Overview

**GNOLEP** is a relational database developed with python to harmonise data from 499 different sources regarding the distribution and origin of non-native Lepidoptera. 

This repository contains: 
  - the Database, stored as a SQLite database in the `Database/` directory;
  - the Individual database tables, in CSV files in the `Database Tables/` directory;
  - the Code used to create the database under `Code/` directory;
  - the originally extracted data, in CSV files in the `Data Raw/` directory.

With future releases, older versions of the database will be stored under the `Previous Versions/` directory to maintain version history and support reproducibility. 

Following the **FAIR principles** (Findable, Accessible, Interoperable, and Reusable) all data was standardised and harmonised using established standards and controlled terminology. Whenever possible terminology used followed Darwin Core terms, while all taxonomy was checked with **GBIF** and cross-checked with **Global Names Verifier**.

The project aims to provide a reliable foundation for research on the distribution, taxonomy, ecology, and spread of non-native Lepidoptera, while maintaining clear provenance for the underlying source data.


## Install and Run


### Required Packages and Libraries

#### Taxonomy Extraction

asyncio; nest_asyncio; tenacity; aiohttp; pandas

#### Database Creation

pandas; sqlite3; os


### Base Install and Run Locally

#### Run Locally
To run only the database locally, download either:
 - GNOLEP.sqlite from the `Database/` directory;
 - or the individual .csv files from the `Database Tables/` directory;

See How to Use the Project for more details.

The database is also available to access through an R package available at: 



#### Rebuilding the Database

To reproduce the database locally from the raw data first clone the repository.

Optionally, before running the workflow the directories `Transformed Data/`, `Intermediate Data Tables/`, `Database Tables/` and `Database/` can be cleared.

If the required packages are not yet installed first run: 0_RequiredLibs.py


Run 1_ObservationData.py 
This script is used to clean and harmonise the observation data present in the `Data Raw/` directory, it will: 
 - standardise and cross-check the taxonomy;
 - Clean the Observations Data;
 - Extract the Taxonomy, References, and list of Established species to retrieve the native distribution;


The native distribution data are stored in `Data Raw/Updated Data/NativeData.csv`. These data were manually compiled and therefore do not originate entirely from the automated workflow. 
Afterwards run 2_NativeData.py to clean it and prepare the `NativeData.csv` for integration.


Run 3_ExtractReferences.py to merge the references between Records Data and Native Data. The resulting table is written to: `Intermediate Data Tables/ReferencesExtracted.csv`. After revise and review manually the references and save the reviewed version as: `Data Raw/Updated Data/RevisedReferences.csv`


Run 4_ImportationPreparation.py to create the final structured relational database and standardise the fields according to **Darwin Core** terminology.


Run 5_DatabaseCreation.py to import each individual table to the final sqlite database file, that will be available at: `Database/GNOLEP.sqlite`


## How to Use the Project

## Credits

## Badges

## How to Contribute
