import pandas as pd
import os
import shutil

# --- Configuration ---
# Source File Paths (from previous steps)
FINAL_STANDARDIZED_MASTER_PATH = os.path.join("02_processed_data", "main_provider_table", "Providers-All Providers_final_standardized.csv")
CONTACT_LABELS_PATH = os.path.join("02_processed_data", "main_provider_table", "provider_contact_and_labels.csv")
MAIN_AIRTABLE_ONLY_DETAILS_SOURCE_PATH = os.path.join("02_processed_data", "main_provider_table", "providers_in_main_airtable_only.csv")

# Output File Paths
MASTER_CONTACT_LIST_OUTPUT_PATH = os.path.join("02_processed_data", "main_provider_table", "master_provider_contact_list.csv")

WORKING_FILES_BASE_DIR = "01_working_file"
AIRTABLE_MASTER_ONLY_NEW_DIR = os.path.join(WORKING_FILES_BASE_DIR, "04_airtable_master_only_details")
AIRTABLE_MASTER_ONLY_NEW_PATH = os.path.join(AIRTABLE_MASTER_ONLY_NEW_DIR, "airtable_master_only_provider_details.csv")

MATCHED_SOURCE_DETAILS_NEW_DIR = os.path.join(WORKING_FILES_BASE_DIR, "05_matched_source_details")
MATCHED_SOURCE_DETAILS_NEW_PATH = os.path.join(MATCHED_SOURCE_DETAILS_NEW_DIR, "matched_provider_details_from_master.csv")

# Column Names
NPI_COL = "National Provider Identifier (NPI)"
FIRST_NAME_COL = "First Name"
LAST_NAME_COL = "Last Name"
EMAIL_COL = "Email Address"
PHONE_COL = "Phone Number"
INTERNAL_LABEL_COL = "Internal Label"

# --- Helper Function for Composite Key ---
def create_composite_name_key(df, first_name_col, last_name_col):
    first = df[first_name_col].astype(str).str.strip().str.lower()
    last = df[last_name_col].astype(str).str.strip().str.lower()
    return last + "_" + first

# --- Main Script ---
def main():
    print("Starting data restructuring and finalization script...")

    # --- Task 1: Create Comprehensive Master Contact List ---
    print(f"\n--- Task 1: Creating Master Contact List ---")
    try:
        df_master_std = pd.read_csv(FINAL_STANDARDIZED_MASTER_PATH)
        print(f"Loaded standardized master: {FINAL_STANDARDIZED_MASTER_PATH} ({len(df_master_std)} rows)")
        df_contact_labels = pd.read_csv(CONTACT_LABELS_PATH)
        print(f"Loaded contact labels: {CONTACT_LABELS_PATH} ({len(df_contact_labels)} rows)")
    except FileNotFoundError as fnf_e:
        print(f"ERROR: Could not load a required file for master contact list: {fnf_e}")
        return
    except Exception as e:
        print(f"ERROR loading files for master contact list: {e}")
        return

    # Prepare for merge - select only key and label from df_contact_labels
    if not all(col in df_contact_labels.columns for col in [FIRST_NAME_COL, LAST_NAME_COL, INTERNAL_LABEL_COL]):
        print(f"ERROR: Required name/label columns not in {CONTACT_LABELS_PATH}")
        return
    df_labels_to_merge = df_contact_labels[[FIRST_NAME_COL, LAST_NAME_COL, INTERNAL_LABEL_COL]].copy()
    df_labels_to_merge['CompositeNameKey'] = create_composite_name_key(df_labels_to_merge, FIRST_NAME_COL, LAST_NAME_COL)
    # Drop duplicates based on the key to ensure one label per name from this source
    df_labels_to_merge.drop_duplicates(subset=['CompositeNameKey'], keep='first', inplace=True)

    if not all(col in df_master_std.columns for col in [FIRST_NAME_COL, LAST_NAME_COL]):
        print(f"ERROR: Required name columns not in {FINAL_STANDARDIZED_MASTER_PATH}")
        return
    df_master_std['CompositeNameKey'] = create_composite_name_key(df_master_std, FIRST_NAME_COL, LAST_NAME_COL)

    # Left merge master_std with labels
    df_merged_contacts = pd.merge(
        df_master_std,
        df_labels_to_merge[[INTERNAL_LABEL_COL, 'CompositeNameKey']],
        on='CompositeNameKey',
        how='left'
    )
    print(f"Merged master with labels, resulting in {len(df_merged_contacts)} rows.")

    # Define and select final columns for the master contact list
    master_contact_list_cols = [LAST_NAME_COL, FIRST_NAME_COL, NPI_COL, EMAIL_COL, PHONE_COL, INTERNAL_LABEL_COL]
    missing_master_cols = [col for col in master_contact_list_cols if col not in df_merged_contacts.columns]
    if missing_master_cols:
        print(f"ERROR: Expected columns for master contact list are missing after merge: {missing_master_cols}")
        print(f"Available columns: {df_merged_contacts.columns.tolist()}")
        return
        
    df_final_master_contact_list = df_merged_contacts[master_contact_list_cols]

    try:
        os.makedirs(os.path.dirname(MASTER_CONTACT_LIST_OUTPUT_PATH), exist_ok=True)
        df_final_master_contact_list.to_csv(MASTER_CONTACT_LIST_OUTPUT_PATH, index=False)
        print(f"Successfully saved master contact list to: {MASTER_CONTACT_LIST_OUTPUT_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save master contact list. Error: {e}")

    # --- Task 2: Move and Rename Detailed File for 'Airtable Master Only' Providers ---
    print(f"\n--- Task 2: Organizing 'Airtable Master Only' Details ---")
    try:
        os.makedirs(AIRTABLE_MASTER_ONLY_NEW_DIR, exist_ok=True)
        # Using shutil.copy to avoid issues if source and dest are same partition, then remove source
        # Or just read and write if we want to ensure it's a new copy and not a move across filesystems
        if os.path.exists(MAIN_AIRTABLE_ONLY_DETAILS_SOURCE_PATH):
            df_airtable_only_src = pd.read_csv(MAIN_AIRTABLE_ONLY_DETAILS_SOURCE_PATH)
            df_airtable_only_src.to_csv(AIRTABLE_MASTER_ONLY_NEW_PATH, index=False)
            print(f"Copied and saved 'Airtable Master Only' details to: {AIRTABLE_MASTER_ONLY_NEW_PATH}")
            # Optionally, remove the old file if this is a true move:
            # os.remove(MAIN_AIRTABLE_ONLY_DETAILS_SOURCE_PATH)
            # print(f"Removed old file: {MAIN_AIRTABLE_ONLY_DETAILS_SOURCE_PATH}")
        else:
            print(f"ERROR: Source file for 'Airtable Master Only' not found at {MAIN_AIRTABLE_ONLY_DETAILS_SOURCE_PATH}")
            
    except Exception as e:
        print(f"ERROR organizing 'Airtable Master Only' details. Error: {e}")

    # --- Task 3: Create Detailed File for Matched Providers from Master ---
    print(f"\n--- Task 3: Creating Detailed File for Matched Providers ---")
    # df_master_std is already loaded and has 'CompositeNameKey'
    # df_contact_labels is also loaded, need to ensure it has 'CompositeNameKey'
    if 'CompositeNameKey' not in df_contact_labels.columns:
         #This was created for df_labels_to_merge, ensure it's on df_contact_labels for this step or recreate
        df_contact_labels['CompositeNameKey'] = create_composite_name_key(df_contact_labels, FIRST_NAME_COL, LAST_NAME_COL)

    contact_labels_keys = set(df_contact_labels['CompositeNameKey'])
    
    # Filter df_master_std for providers whose key IS in contact_labels_keys
    # The df_master_std used here still has its 'CompositeNameKey' from Task 1
    df_matched_details = df_master_std[df_master_std['CompositeNameKey'].isin(contact_labels_keys)].copy()
    print(f"Found {len(df_matched_details)} matched providers for detailed file.")

    # Drop the helper key column before saving
    df_matched_details.drop(columns=['CompositeNameKey'], inplace=True, errors='ignore')
    # also drop from df_master_std if it's used further, though it isn't here
    df_master_std.drop(columns=['CompositeNameKey'], inplace=True, errors='ignore') 

    if not df_matched_details.empty:
        try:
            os.makedirs(MATCHED_SOURCE_DETAILS_NEW_DIR, exist_ok=True)
            df_matched_details.to_csv(MATCHED_SOURCE_DETAILS_NEW_PATH, index=False)
            print(f"Successfully saved matched provider details from master to: {MATCHED_SOURCE_DETAILS_NEW_PATH}")
        except Exception as e:
            print(f"ERROR: Could not save matched provider details. Error: {e}")
    else:
        print("No matched providers found to create detailed file.")

    print("\nRestructuring script finished.")

if __name__ == "__main__":
    main() 