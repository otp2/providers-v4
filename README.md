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
*   **Salesforce Picklists:** Standard picklists for Credentials, Ages, Genders, and Modalities loaded.
*   **Name Reconciliation:**
    *   Northshore names cleaned and reconciled against the primary mapping list (derived from legacy Airtable).
    *   Pulse names extracted, cleaned, consolidated, and reconciled against the primary mapping list.
    *   All Pulse and Northshore providers are now accounted for in the primary mapping list.
*   **Unmatched Provider Identification:** Providers listed in the primary mapping file but *not* found in Pulse or Northshore sources have been identified and saved separately.
*   **Initial Data Cleaning:** Basic formatting cleanup applied to Salesforce picklists and source files (whitespace, blank rows, specific character issues).
*   **File Structure Reorganization:** Directory structure updated with numbered prefixes for better organization and clarity.

## Project Structure

```
├── 00_source_data/
│   ├── 00_original_providers_all_providers/  # Original Airtable CSV data
│   ├── 01_pulse_data/                  # Raw Pulse system exports
│   │   ├── pulse_bhi/
│   │   ├── pulse_counseling/
│   │   └── pulse_mm/
│   └── 02_guidebook/                   # Guidebook data
├── 01_working_file/                  # Files related to mapping and reconciliation
│   ├── 00_archive/                     # Archive of older working files
│   ├── 01_not_in_pulses_or_guidebook/  # Providers not found in current sources
│   └── 02_in_pulse_or_guidebook/       # Matched providers from current sources
├── 02_processed_data/                # Processed and consolidated data
│   └── main_provider_table/            # Main consolidated provider data
├── 03_salesforce_picklist/           # Canonical picklists from Salesforce
│   ├── salesforce_ages.csv
│   ├── salesforce_credentials.csv
│   ├── salesforce_genders.csv
│   └── salesforce_treatment_modialities.csv
├── 04_scripts/                       # Contains helper scripts
│   └── archive/                        # Older versions of scripts
├── 05_documentation/                 # Project documentation
│   ├── Project_Goals_and_Scope.md
│   ├── Data_Sources_and_Schema.md
│   ├── Processing_Log_and_Methodology.md
│   └── data_restructuring_plan.md
├── .gitignore
├── README.md
```

## Key Documentation

*   [Project Goals and Scope](./05_documentation/Project_Goals_and_Scope.md)
*   [Data Sources and Schema](./05_documentation/Data_Sources_and_Schema.md)
*   [Processing Log and Methodology](./05_documentation/Processing_Log_and_Methodology.md)
*   [Data Restructuring Plan](./05_documentation/data_restructuring_plan.md)
*   [Next Steps and Considerations](./05_documentation/Next_Steps_and_Considerations.md)

## Next Steps Overview

1.  **Salesforce Picklist Mapping:** Map source data fields (Credentials, Ages, etc.) to the standard Salesforce lists.
2.  **NPI Lookup & Validation:** Verify and find missing NPIs for providers.
3.  **Field Mapping:** Map remaining relevant fields from source data to the target schema.
4.  **Data Validation & Cleanup:** Perform final consistency checks and data cleaning.
5.  **Airtable Preparation:** Format data for import into the new Airtable base structure.

See [Next Steps and Considerations](./05_documentation/Next_Steps_and_Considerations.md) for detailed information. 