import pandas as pd
import os

# --- Configuration ---
UPDATED_NAMES_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "Providers-All Providers_updated_names.csv")
FINAL_STANDARDIZED_OUTPUT_PATH = os.path.join("02_processed_data", "main_provider_table", "Providers-All Providers_final_standardized.csv")

CONTACT_LABELS_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "provider_contact_and_labels.csv")
MAIN_AIRTABLE_ONLY_OUTPUT_PATH = os.path.join("02_processed_data", "main_provider_table", "providers_in_main_airtable_only.csv")

# Column names for NPI and name components (must be consistent across files after standardization)
NPI_COL = "National Provider Identifier (NPI)"
FIRST_NAME_COL = "First Name"
LAST_NAME_COL = "Last Name"

# --- Helper Functions ---
def clean_npi(npi_value):
    if pd.isna(npi_value):
        return None # Represent missing NPIs as None (which becomes blank in CSV)
    npi_str = str(npi_value)
    if npi_str.endswith(".0"):
        return npi_str[:-2]
    return npi_str

def create_composite_name_key(df, first_name_col, last_name_col):
    """Creates a standardized composite key from first and last names for matching."""
    # Ensure columns are string and stripped, then create key
    first = df[first_name_col].astype(str).str.strip().str.lower()
    last = df[last_name_col].astype(str).str.strip().str.lower()
    return last + "_" + first

# --- Main Script ---
def main():
    print("Starting master file finalization and gap identification script...")

    # --- Part A: Finalize the master standardized provider list ---
    print(f"\n--- Part A: Processing {UPDATED_NAMES_FILE_PATH} ---")
    try:
        df_master_updated_names = pd.read_csv(UPDATED_NAMES_FILE_PATH)
        print(f"Successfully loaded: {UPDATED_NAMES_FILE_PATH} ({len(df_master_updated_names)} rows)")
    except FileNotFoundError:
        print(f"ERROR: File not found at {UPDATED_NAMES_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERROR: Could not load file {UPDATED_NAMES_FILE_PATH}. Error: {e}")
        return

    # Clean NPI column
    if NPI_COL in df_master_updated_names.columns:
        print(f"Cleaning NPI column: {NPI_COL} in master data")
        df_master_updated_names[NPI_COL] = df_master_updated_names[NPI_COL].apply(clean_npi)
    else:
        print(f"Warning: NPI column '{NPI_COL}' not found in {UPDATED_NAMES_FILE_PATH}.")

    # Save this as the final standardized master data
    try:
        os.makedirs(os.path.dirname(FINAL_STANDARDIZED_OUTPUT_PATH), exist_ok=True)
        df_master_updated_names.to_csv(FINAL_STANDARDIZED_OUTPUT_PATH, index=False)
        print(f"Successfully saved final standardized master data to: {FINAL_STANDARDIZED_OUTPUT_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save final standardized master data. Error: {e}")
        return # Stop if we can't save this critical intermediate file

    # --- Part B: Identify providers in master but not in contact_labels ---
    print(f"\n--- Part B: Identifying providers in master but not in contact_labels ---")
    try:
        df_contact_labels = pd.read_csv(CONTACT_LABELS_FILE_PATH)
        print(f"Successfully loaded: {CONTACT_LABELS_FILE_PATH} ({len(df_contact_labels)} rows)")
    except FileNotFoundError:
        print(f"ERROR: File not found at {CONTACT_LABELS_FILE_PATH}. Ensure previous script ran successfully.")
        return
    except Exception as e:
        print(f"ERROR: Could not load file {CONTACT_LABELS_FILE_PATH}. Error: {e}")
        return

    # Create composite name keys for comparison
    # df_master_updated_names is already loaded and NPI-cleaned
    if not all(col in df_master_updated_names.columns for col in [FIRST_NAME_COL, LAST_NAME_COL]):
        print(f"ERROR: Name columns ('{FIRST_NAME_COL}', '{LAST_NAME_COL}') not found in {FINAL_STANDARDIZED_OUTPUT_PATH}.")
        return
    df_master_updated_names['CompositeNameKey'] = create_composite_name_key(df_master_updated_names, FIRST_NAME_COL, LAST_NAME_COL)
    
    if not all(col in df_contact_labels.columns for col in [FIRST_NAME_COL, LAST_NAME_COL]):
        print(f"ERROR: Name columns ('{FIRST_NAME_COL}', '{LAST_NAME_COL}') not found in {CONTACT_LABELS_FILE_PATH}.")
        return
    df_contact_labels['CompositeNameKey'] = create_composite_name_key(df_contact_labels, FIRST_NAME_COL, LAST_NAME_COL)

    # Get the set of keys from contact_labels for efficient lookup
    contact_labels_keys = set(df_contact_labels['CompositeNameKey'])

    # Filter df_master_updated_names for providers whose key is not in contact_labels_keys
    df_in_master_only = df_master_updated_names[~df_master_updated_names['CompositeNameKey'].isin(contact_labels_keys)].copy()
    print(f"Found {len(df_in_master_only)} providers present in '{FINAL_STANDARDIZED_OUTPUT_PATH}' but not in '{CONTACT_LABELS_FILE_PATH}'.")

    # Drop the helper CompositeNameKey column before saving
    df_in_master_only.drop(columns=['CompositeNameKey'], inplace=True, errors='ignore')
    df_master_updated_names.drop(columns=['CompositeNameKey'], inplace=True, errors='ignore') # also from the df that was saved as _final_standardized

    # Save the result
    if not df_in_master_only.empty:
        try:
            os.makedirs(os.path.dirname(MAIN_AIRTABLE_ONLY_OUTPUT_PATH), exist_ok=True)
            df_in_master_only.to_csv(MAIN_AIRTABLE_ONLY_OUTPUT_PATH, index=False)
            print(f"Successfully saved providers unique to master data to: {MAIN_AIRTABLE_ONLY_OUTPUT_PATH}")
        except Exception as e:
            print(f"ERROR: Could not save providers unique to master data. Error: {e}")
    else:
        print("No providers found that were unique to the master data file.")

    print("\nScript finished.")

if __name__ == "__main__":
    main() 