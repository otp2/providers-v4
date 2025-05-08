import pandas as pd
import os

# --- Configuration ---
# File paths
AIRTABLE_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "working_airtable.csv")
UPDATED_PROVIDERS_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "Providers-All Providers_updated_names.csv")
OUTPUT_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "provider_contact_and_labels.csv")

# Column names from working_airtable.csv
AIRTABLE_FIRST_NAME_COL = "First Name"
AIRTABLE_LAST_NAME_COL = "Last Name"
AIRTABLE_LABEL_COL = "Internal Label"

# Column names from Providers-All Providers_updated_names.csv
DETAILS_FIRST_NAME_COL = "First Name"
DETAILS_LAST_NAME_COL = "Last Name"
DETAILS_NPI_COL = "National Provider Identifier (NPI)"
DETAILS_EMAIL_COL = "Email Address"
DETAILS_PHONE_COL = "Phone Number"

# Columns for the final output and their order
FINAL_OUTPUT_COLUMNS = [
    AIRTABLE_LAST_NAME_COL, # Will come from airtable_df after merge
    AIRTABLE_FIRST_NAME_COL, # Will come from airtable_df after merge
    DETAILS_NPI_COL,
    DETAILS_EMAIL_COL,
    DETAILS_PHONE_COL,
    AIRTABLE_LABEL_COL
]

# --- Helper Functions ---
def clean_npi(npi_value):
    if pd.isna(npi_value):
        return None # Represent missing NPIs as None (which becomes blank in CSV)
    npi_str = str(npi_value)
    if npi_str.endswith(".0"):
        return npi_str[:-2]
    return npi_str

# --- Main Script ---
def main():
    print("Starting provider detail combination script...")

    # Load data
    try:
        df_airtable = pd.read_csv(AIRTABLE_FILE_PATH)
        print(f"Successfully loaded airtable file: {AIRTABLE_FILE_PATH} ({len(df_airtable)} rows)")
    except FileNotFoundError:
        print(f"ERROR: Airtable file not found at {AIRTABLE_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERROR: Could not load airtable file {AIRTABLE_FILE_PATH}. Error: {e}")
        return

    try:
        df_provider_details = pd.read_csv(UPDATED_PROVIDERS_FILE_PATH)
        print(f"Successfully loaded updated provider details file: {UPDATED_PROVIDERS_FILE_PATH} ({len(df_provider_details)} rows)")
    except FileNotFoundError:
        print(f"ERROR: Updated provider details file not found at {UPDATED_PROVIDERS_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERROR: Could not load updated provider details file {UPDATED_PROVIDERS_FILE_PATH}. Error: {e}")
        return

    # Prepare for merge: ensure merge key columns are strings and stripped
    airtable_key_cols = [AIRTABLE_FIRST_NAME_COL, AIRTABLE_LAST_NAME_COL]
    details_key_cols = [DETAILS_FIRST_NAME_COL, DETAILS_LAST_NAME_COL]

    for col in airtable_key_cols:
        if col in df_airtable.columns:
            df_airtable[col] = df_airtable[col].astype(str).str.strip()
        else:
            print(f"ERROR: Merge key column '{col}' not found in {AIRTABLE_FILE_PATH}")
            return
            
    for col in details_key_cols:
        if col in df_provider_details.columns:
            df_provider_details[col] = df_provider_details[col].astype(str).str.strip()
        else:
            print(f"ERROR: Merge key column '{col}' not found in {UPDATED_PROVIDERS_FILE_PATH}")
            return

    # Select only necessary columns from df_provider_details to avoid duplicate columns after merge (except keys)
    cols_to_select_from_details = details_key_cols + [DETAILS_NPI_COL, DETAILS_EMAIL_COL, DETAILS_PHONE_COL]
    # Ensure all selected columns exist
    missing_cols_details = [col for col in cols_to_select_from_details if col not in df_provider_details.columns]
    if missing_cols_details:
        print(f"ERROR: Following columns are missing in {UPDATED_PROVIDERS_FILE_PATH}: {', '.join(missing_cols_details)}")
        return
        
    df_provider_details_selected = df_provider_details[cols_to_select_from_details].copy()
    
    # Handle potential duplicates in the right table (df_provider_details_selected) before merging
    # Keep the first occurrence if names are duplicated, as names should now be aligned with the truth file
    df_provider_details_selected.drop_duplicates(subset=details_key_cols, keep='first', inplace=True)
    print(f"Provider details (right side of merge) reduced to {len(df_provider_details_selected)} rows after dropping duplicates on name keys.")

    # Perform the left merge
    print(f"Merging {len(df_airtable)} rows from airtable with {len(df_provider_details_selected)} unique name rows from provider details...")
    df_combined = pd.merge(
        df_airtable,
        df_provider_details_selected,
        left_on=airtable_key_cols,
        right_on=details_key_cols,
        how='left'
    )
    print(f"Merge resulted in {len(df_combined)} rows.")

    # Ensure all final output columns exist in the merged dataframe
    missing_final_cols = [col for col in FINAL_OUTPUT_COLUMNS if col not in df_combined.columns]
    if missing_final_cols:
        print(f"ERROR: Following expected final columns are missing after merge: {', '.join(missing_final_cols)}")
        # print("Available columns after merge:", df_combined.columns.tolist()) # For debugging
        return

    # Select and reorder columns for the final output
    df_final_output = df_combined[FINAL_OUTPUT_COLUMNS].copy() # Use .copy() to avoid SettingWithCopyWarning

    # Clean NPI column in the final output
    if DETAILS_NPI_COL in df_final_output.columns:
        print(f"Cleaning NPI column: {DETAILS_NPI_COL}")
        df_final_output[DETAILS_NPI_COL] = df_final_output[DETAILS_NPI_COL].apply(clean_npi)
    else:
        print(f"Warning: NPI column '{DETAILS_NPI_COL}' not found in final output for cleaning.")

    # Save the combined DataFrame
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
        df_final_output.to_csv(OUTPUT_FILE_PATH, index=False)
        print(f"Successfully saved combined provider details to: {OUTPUT_FILE_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save combined provider details file. Error: {e}")

if __name__ == "__main__":
    main() 