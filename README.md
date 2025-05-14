# Provider Data Consolidation & Standardization (providers-v4)

This project aims to consolidate, clean, standardize, and map provider data from various historical and current sources into a reliable dataset suitable for a new Airtable base. The goal is to create a single source of truth aligned with Salesforce standards.

## Project Goal

To create a unified, clean, and accurate provider dataset by:
1.  Ingesting data from legacy Airtable exports, current Pulse system exports, and Northshore provider lists.
2.  Reconciling provider identities across these sources using NPI and name matching.
3.  Standardizing key data points (Credentials, Ages Seen, Gender Identity, Treatment Modalities) against canonical Salesforce picklists.
4.  Preparing the consolidated data for eventual import into a new, structured Airtable base.

For a detailed explanation of project goals, see [Project Goals and Scope](./05_documentation/Project_Goals_and_Scope.md).

## Current Status

*   **Data Ingestion:** Legacy Airtable, Pulse (BHI, Counseling, MM), and Northshore data loaded.
*   **Initial Data Transformation:** All three Pulse data sources (BHI, Counseling, MM) have been combined into a single working file in the 01_working_data_transformation directory.
*   **Column Standardization:** Provider Type data has been integrated within the Internal Label field to reduce redundancy.
*   **NPI Integration:** Added NPI numbers from the standardized provider list to all providers in the working dataset.
*   **Location Information Update:** Added comprehensive location details (building names, addresses, phone numbers) to providers based on their primary locations.
*   **Next Phase:** Data mapping against Salesforce picklists and field standardization.

## Project Structure

```
├── 00_source_data/
│   ├── 00_original_providers_all_providers/  # Original Airtable CSV data
│   ├── 01_pulse_data/                  # Raw Pulse system exports
│   │   ├── pulse_bhi/
│   │   ├── pulse_counseling/
│   │   └── pulse_mm/
│   └── 02_guidebook/                   # Guidebook data
├── 01_working_data_transformation/     # Files related to data transformation
│   ├── 00_working_data_transformation/   # Active transformation files
│   │   ├── working_pulse_v1.csv         # Combined Pulse data (BHI, Counseling, MM)
│   │   └── working_pulse_v2.csv         # Enhanced data with NPI and location details
│   └── archive/                        # Archive of older working files
├── 02_processed_data/                # Processed and consolidated data files
├── 03_salesforce_picklist/           # Canonical picklists from Salesforce
├── 04_python_scripts/                # Contains helper scripts
│   └── archive/                        # Older versions of scripts
├── 05_documentation/                 # Project documentation
│   ├── Project_Goals_and_Scope.md
│   ├── Data_Sources_and_Schema.md
│   ├── Processing_Log_and_Methodology.md
│   ├── data_restructuring_plan.md
│   └── Next_Steps_and_Considerations.md
├── README.md
```

## Key Documentation

*   [Project Goals and Scope](./05_documentation/Project_Goals_and_Scope.md)
*   [Data Sources and Schema](./05_documentation/Data_Sources_and_Schema.md)
*   [Processing Log and Methodology](./05_documentation/Processing_Log_and_Methodology.md)
*   [Data Restructuring Plan](./05_documentation/data_restructuring_plan.md)
*   [Next Steps and Considerations](./05_documentation/Next_Steps_and_Considerations.md)

## Recent Updates

* Added NPI numbers as a unique identifier to all providers in the working dataset
* Updated provider names in the standardized provider list for better matching
* Added location information (building names, addresses, phone numbers) to all providers
* Created and updated Python scripts for data transformation and matching

## Next Steps Overview

1.  **Field Standardization:** Standardize all remaining fields in the combined dataset.
2.  **Salesforce Picklist Mapping:** Map source data fields (Credentials, Ages, etc.) to the standard Salesforce lists.
3.  **Field Mapping:** Map remaining relevant fields from source data to the target schema.
4.  **Data Validation & Cleanup:** Perform final consistency checks and data cleaning.
5.  **Airtable Preparation:** Format data for import into the new Airtable base structure.

See [Next Steps and Considerations](./05_documentation/Next_Steps_and_Considerations.md) for detailed information. 