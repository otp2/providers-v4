import pandas as pd
import os
import re

# --- Configuration ---
# Input Files
MASTER_CONTACT_LIST_PATH = os.path.join("02_processed_data", "main_provider_table", "master_provider_contact_list.csv")
GUIDEBOOK_PATH = os.path.join("00_source_data", "guidebook", "guidebook.csv")
PULSE_BHI_PATH = os.path.join("00_source_data", "pulse_data", "pulse_bhi", "pulse_bhi.csv")
PULSE_COUNSELING_PATH = os.path.join("00_source_data", "pulse_data", "pulse_counseling", "pulse_counseling.csv")
PULSE_MM_PATH = os.path.join("00_source_data", "pulse_data", "pulse_mm", "pulse_mm.csv")

SOURCE_FILES_CONFIG = [
    {"path": GUIDEBOOK_PATH, "first_name_col": "First Name", "last_name_col": "Last Name"},
    {"path": PULSE_BHI_PATH, "first_name_col": "First Name", "last_name_col": "Last Name", "phone_col": "Patient Facing Number"},
    {"path": PULSE_COUNSELING_PATH, "first_name_col": "First Name", "last_name_col": "Last Name"},
    {"path": PULSE_MM_PATH, "first_name_col": "First Name", "last_name_col": "Last Name"}
]

# Output Files
UPDATED_MASTER_CONTACT_LIST_PATH = MASTER_CONTACT_LIST_PATH # Overwrite the existing file
MISSING_PROVIDERS_REPORT_PATH = os.path.join("02_processed_data", "main_provider_table", "missing_source_providers_report.txt")
BHI_PHONE_UPDATE_REPORT_PATH = os.path.join("02_processed_data", "main_provider_table", "bhi_phone_update_report.txt")

# Column Names in Master List
MASTER_FIRST_NAME_COL = "First Name"
MASTER_LAST_NAME_COL = "Last Name"
MASTER_PHONE_COL = "Phone Number"
MASTER_INTERNAL_LABEL_COL = "Internal Label"

# --- Helper Functions ---
def create_composite_name_key(df, first_name_col, last_name_col):
    first = df[first_name_col].astype(str).str.strip().str.lower()
    last = df[last_name_col].astype(str).str.strip().str.lower()
    return last + "_" + first

def clean_phone_number(phone_str):
    """Removes non-digit characters from a phone number string."""
    if pd.isna(phone_str):
        return ""
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', str(phone_str))
    return cleaned

# --- Main Script ---
def main():
    print("Starting source validation and BHI phone update script...")
    all_source_normalized_names = set()
    bhi_phone_map = {}
    missing_providers_report = []
    bhi_update_report = []

    # --- Task 1: Load and Consolidate Source Names & BHI Phones ---
    print("\n--- Task 1: Loading and consolidating source data ---")
    for config in SOURCE_FILES_CONFIG:
        file_path = config["path"]
        first_name_col = config["first_name_col"]
        last_name_col = config["last_name_col"]
        phone_col = config.get("phone_col") # Get phone column name if it exists

        try:
            df_source = pd.read_csv(file_path)
            print(f"Loaded source file: {file_path} ({len(df_source)} rows)")

            # Check for required name columns
            if not all(col in df_source.columns for col in [first_name_col, last_name_col]):
                print(f"Warning: Skipping file {file_path} due to missing name columns ('{first_name_col}' or '{last_name_col}').")
                continue

            # Create composite key
            df_source['CompositeNameKey'] = create_composite_name_key(df_source, first_name_col, last_name_col)
            
            # Add valid names to the set
            valid_keys = df_source[df_source['CompositeNameKey'] != '_']['CompositeNameKey'].unique()
            all_source_normalized_names.update(valid_keys)
            
            # If this is the BHI file and has a phone column, populate the phone map
            if file_path == PULSE_BHI_PATH and phone_col and phone_col in df_source.columns:
                print(f"Processing BHI phone numbers from column: {phone_col}")
                # Drop duplicates based on name key, keeping the first phone number encountered
                df_bhi_unique = df_source.drop_duplicates(subset=['CompositeNameKey'], keep='first')
                for _, row in df_bhi_unique.iterrows():
                    key = row['CompositeNameKey']
                    phone = row[phone_col]
                    if key != '_' and pd.notna(phone):
                        bhi_phone_map[key] = str(phone) # Store as string initially
                print(f"Created BHI phone map with {len(bhi_phone_map)} entries.")
                
        except FileNotFoundError:
            print(f"Warning: Source file not found: {file_path}")
        except Exception as e:
            print(f"Warning: Could not process source file {file_path}. Error: {e}")
            
    print(f"Consolidated unique normalized names from sources: {len(all_source_normalized_names)}")

    # --- Task 2: Load Master List and Identify Missing Providers ---
    print("\n--- Task 2: Loading master list and checking for missing providers ---")
    try:
        df_master = pd.read_csv(MASTER_CONTACT_LIST_PATH)
        print(f"Loaded master contact list: {MASTER_CONTACT_LIST_PATH} ({len(df_master)} rows)")
    except FileNotFoundError:
        print(f"ERROR: Master contact list not found at {MASTER_CONTACT_LIST_PATH}. Cannot proceed.")
        return
    except Exception as e:
        print(f"ERROR: Could not load master contact list {MASTER_CONTACT_LIST_PATH}. Error: {e}")
        return

    if not all(col in df_master.columns for col in [MASTER_FIRST_NAME_COL, MASTER_LAST_NAME_COL]):
        print(f"ERROR: Master list is missing required name columns ('{MASTER_FIRST_NAME_COL}' or '{MASTER_LAST_NAME_COL}'). Cannot proceed.")
        return
        
    df_master['CompositeNameKey'] = create_composite_name_key(df_master, MASTER_FIRST_NAME_COL, MASTER_LAST_NAME_COL)
    master_normalized_names = set(df_master['CompositeNameKey'])

    missing_from_master = all_source_normalized_names - master_normalized_names
    
    missing_providers_report.append("Providers in Source Files Missing from Master Contact List\n")
    missing_providers_report.append("="*60 + "\n")
    if missing_from_master:
        print(f"Found {len(missing_from_master)} providers from sources potentially missing in the master list.")
        for name_key in sorted(list(missing_from_master)):
            missing_providers_report.append(f"- {name_key}\n")
    else:
        print("All providers from source files appear to be present in the master contact list.")
        missing_providers_report.append("No missing providers found.\n")

    # --- Task 3: Update BHI Phone Numbers in Master List ---
    print("\n--- Task 3: Updating BHI phone numbers in master list ---")
    bhi_update_report.append("BHI Phone Number Update Report\n")
    bhi_update_report.append("="*60 + "\n")
    update_count = 0
    processed_indices = set() # To handle potential duplicate names in master list with BHI label

    if MASTER_PHONE_COL not in df_master.columns:
        print(f"Warning: Master phone column '{MASTER_PHONE_COL}' not found. Skipping BHI phone update.")
        bhi_update_report.append("Skipped: Master phone column not found.\n")
    elif MASTER_INTERNAL_LABEL_COL not in df_master.columns:
        print(f"Warning: Master internal label column '{MASTER_INTERNAL_LABEL_COL}' not found. Skipping BHI phone update.")
        bhi_update_report.append("Skipped: Master internal label column not found.\n")
    elif not bhi_phone_map:
        print("Warning: BHI phone map is empty. Skipping BHI phone update.")
        bhi_update_report.append("Skipped: No BHI phone numbers loaded.\n")
    else:
        for index, row in df_master.iterrows():
            # Check if the row has already been processed (handles duplicates in master with BHI label)
            if index in processed_indices:
                continue

            label = row[MASTER_INTERNAL_LABEL_COL]
            name_key = row['CompositeNameKey']
            
            # Process only if label is BHI and name_key is valid
            if pd.notna(label) and label == "Behavioral Health Integration" and name_key != '_':
                # Find all master rows with the same key (handle duplicates)
                matching_master_indices = df_master[df_master['CompositeNameKey'] == name_key].index
                
                for master_idx in matching_master_indices:
                    if master_idx in processed_indices:
                        continue # Skip if this specific duplicate row was already processed

                    current_master_phone = df_master.loc[master_idx, MASTER_PHONE_COL]
                    cleaned_current_phone = clean_phone_number(current_master_phone)
                    
                    if name_key in bhi_phone_map:
                        bhi_phone_str = bhi_phone_map[name_key]
                        cleaned_bhi_phone = clean_phone_number(bhi_phone_str)
                        
                        # Update if BHI phone is valid (10 digits) and different from current
                        if len(cleaned_bhi_phone) == 10 and cleaned_bhi_phone != cleaned_current_phone:
                            original_phone = current_master_phone if pd.notna(current_master_phone) else "<blank>"
                            # Update the DataFrame
                            df_master.loc[master_idx, MASTER_PHONE_COL] = bhi_phone_str # Use original BHI string for format consistency
                            update_count += 1
                            log_msg = (f"- Updated index {master_idx} (Name Key: {name_key}): \n" 
                                       f"  Old Phone: '{original_phone}' \n" 
                                       f"  New Phone: '{bhi_phone_str}' (from BHI source)\n")
                            bhi_update_report.append(log_msg)
                    processed_indices.add(master_idx)

        print(f"Completed BHI phone update check. Updated {update_count} phone numbers.")
        if update_count == 0:
            bhi_update_report.append("No phone numbers required updating.\n")

    # --- Task 4: Save Outputs ---
    print("\n--- Task 4: Saving outputs ---")
    # Save the potentially updated master list
    try:
        df_master.drop(columns=['CompositeNameKey'], inplace=True, errors='ignore') # Clean up helper column
        df_master.to_csv(UPDATED_MASTER_CONTACT_LIST_PATH, index=False)
        print(f"Successfully saved updated master contact list to: {UPDATED_MASTER_CONTACT_LIST_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save updated master contact list. Error: {e}")

    # Save the missing providers report
    try:
        os.makedirs(os.path.dirname(MISSING_PROVIDERS_REPORT_PATH), exist_ok=True)
        with open(MISSING_PROVIDERS_REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("".join(missing_providers_report))
        print(f"Successfully saved missing providers report to: {MISSING_PROVIDERS_REPORT_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save missing providers report. Error: {e}")
        
    # Save the BHI phone update report
    try:
        os.makedirs(os.path.dirname(BHI_PHONE_UPDATE_REPORT_PATH), exist_ok=True)
        with open(BHI_PHONE_UPDATE_REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("".join(bhi_update_report))
        print(f"Successfully saved BHI phone update report to: {BHI_PHONE_UPDATE_REPORT_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save BHI phone update report. Error: {e}")

    print("\nScript finished.")

if __name__ == "__main__":
    main() 