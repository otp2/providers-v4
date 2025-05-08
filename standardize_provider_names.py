import pandas as pd
from thefuzz import fuzz, process
import os

# --- Configuration ---
# File paths - adjust if your script is not in the project root or file locations change
TRUTH_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "working_airtable.csv")
TARGET_FILE_PATH = os.path.join("00_source_data", "airtable_monolithic", "Providers-All Providers.csv")
OUTPUT_TARGET_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "Providers-All Providers_updated_names.csv")
REPORT_FILE_PATH = os.path.join("02_processed_data", "main_provider_table", "name_standardization_report.txt")

# Column names
TRUTH_FIRST_NAME_COL = "First Name"
TRUTH_LAST_NAME_COL = "Last Name"

TARGET_NPI_COL = "National Provider Identifier (NPI)"
TARGET_FIRST_NAME_COL = "First Name"
TARGET_LAST_NAME_COL = "Last Name"
TARGET_FULL_NAME_COL = "Provider Full Name"

# Fuzzy matching threshold (0-100). Higher means stricter matching.
MATCH_THRESHOLD = 90

# --- Helper Functions ---
def normalize_name(first_name, last_name):
    """Converts first and last names to a standardized format for matching."""
    fn = str(first_name).lower().strip() if pd.notna(first_name) else ""
    ln = str(last_name).lower().strip() if pd.notna(last_name) else ""
    # Consistent order for matching, e.g., "lastname, firstname"
    if fn and ln:
        return f"{ln}, {fn}"
    elif ln:
        return ln
    elif fn:
        return fn
    return ""

# --- Main Script ---
def main():
    report_content = []
    report_content.append("Name Standardization Process Report\\n")
    report_content.append("="*30 + "\\n")

    # Load data
    try:
        df_truth = pd.read_csv(TRUTH_FILE_PATH)
        report_content.append(f"Successfully loaded truth file: {TRUTH_FILE_PATH}\\n")
        report_content.append(f"  - Rows in truth file: {len(df_truth)}\\n")
    except FileNotFoundError:
        report_content.append(f"ERROR: Truth file not found at {TRUTH_FILE_PATH}\\n")
        print(f"ERROR: Truth file not found at {TRUTH_FILE_PATH}")
        return
    except Exception as e:
        report_content.append(f"ERROR: Could not load truth file {TRUTH_FILE_PATH}. Error: {e}\\n")
        print(f"ERROR: Could not load truth file {TRUTH_FILE_PATH}. Error: {e}")
        return

    try:
        df_target = pd.read_csv(TARGET_FILE_PATH)
        report_content.append(f"Successfully loaded target file: {TARGET_FILE_PATH}\\n")
        report_content.append(f"  - Rows in target file: {len(df_target)}\\n")
    except FileNotFoundError:
        report_content.append(f"ERROR: Target file not found at {TARGET_FILE_PATH}\\n")
        print(f"ERROR: Target file not found at {TARGET_FILE_PATH}")
        return
    except Exception as e:
        report_content.append(f"ERROR: Could not load target file {TARGET_FILE_PATH}. Error: {e}\\n")
        print(f"ERROR: Could not load target file {TARGET_FILE_PATH}. Error: {e}")
        return

    # Prepare normalized names for matching
    # Ensure name columns are string type for normalization and updates
    df_truth[TRUTH_FIRST_NAME_COL] = df_truth[TRUTH_FIRST_NAME_COL].astype(str)
    df_truth[TRUTH_LAST_NAME_COL] = df_truth[TRUTH_LAST_NAME_COL].astype(str)
    df_target[TARGET_FIRST_NAME_COL] = df_target[TARGET_FIRST_NAME_COL].astype(str)
    df_target[TARGET_LAST_NAME_COL] = df_target[TARGET_LAST_NAME_COL].astype(str)
    df_target[TARGET_FULL_NAME_COL] = df_target[TARGET_FULL_NAME_COL].astype(str)


    df_truth['Normalized_Name_Truth'] = df_truth.apply(
        lambda row: normalize_name(row[TRUTH_FIRST_NAME_COL], row[TRUTH_LAST_NAME_COL]), axis=1
    )
    df_target['Normalized_Name_Target'] = df_target.apply(
        lambda row: normalize_name(row[TARGET_FIRST_NAME_COL], row[TARGET_LAST_NAME_COL]), axis=1
    )

    # Create a list of choices for fuzzy matching from the target DataFrame
    target_names_list = df_target['Normalized_Name_Target'].tolist()
    
    # Keep track of updates and issues
    updated_target_indices = set()
    unmatched_truth_providers = []
    ambiguous_matches = []
    updates_log = [] # To log specific changes

    report_content.append(f"\\n--- Matching and Updating (Threshold: {MATCH_THRESHOLD}) ---\\n")

    for index_truth, row_truth in df_truth.iterrows():
        truth_normalized_name = row_truth['Normalized_Name_Truth']
        truth_first = row_truth[TRUTH_FIRST_NAME_COL]
        truth_last = row_truth[TRUTH_LAST_NAME_COL]

        if not truth_normalized_name: # Skip if truth name is empty
            report_content.append(f"Skipping empty normalized name in truth file at index {index_truth}. Original: '{truth_first}' '{truth_last}'\\n")
            continue

        # Find the best match in the target DataFrame
        # process.extractOne returns (choice, score, index_in_original_list) when scorer is fuzz.WRatio
        # If target_names_list can have duplicates, index_in_original_list refers to its first occurrence.
        # It's better to use df_target.index directly if extractOne can return it or match back.
        # For simplicity with extractOne, we'll get the matched string and then find its index in df_target.
        
        # We need to handle cases where target_names_list might be empty or too small
        if not target_names_list:
            unmatched_truth_providers.append({
                "truth_name": f"{truth_first} {truth_last}",
                "reason": "Target list for matching is empty."
            })
            continue

        match_result = process.extractOne(truth_normalized_name, target_names_list, scorer=fuzz.WRatio, score_cutoff=MATCH_THRESHOLD)

        if match_result:
            matched_name_in_target_list, score = match_result[0], match_result[1]
            
            # Find all indices in df_target that correspond to this matched_name_in_target_list
            # This handles if multiple providers in df_target have the exact same normalized name
            possible_target_indices = df_target[df_target['Normalized_Name_Target'] == matched_name_in_target_list].index.tolist()

            if not possible_target_indices:
                # This case should ideally not happen if matched_name_in_target_list came from target_names_list
                unmatched_truth_providers.append({
                    "truth_name": f"{truth_first} {truth_last}",
                    "reason": f"Internal error: Matched name '{matched_name_in_target_list}' not found back in target DataFrame."
                })
                continue

            # For now, let's take the first available index. More sophisticated logic could be added here.
            # e.g. if multiple target rows match, and one is already updated, pick another.
            # Or, if NPIs were available and somewhat reliable, use them as a tie-breaker.
            
            target_idx_to_update = -1
            for pt_idx in possible_target_indices:
                if pt_idx not in updated_target_indices:
                    target_idx_to_update = pt_idx
                    break
            
            if target_idx_to_update != -1:
                original_target_first = df_target.loc[target_idx_to_update, TARGET_FIRST_NAME_COL]
                original_target_last = df_target.loc[target_idx_to_update, TARGET_LAST_NAME_COL]
                original_target_full = df_target.loc[target_idx_to_update, TARGET_FULL_NAME_COL]
                original_target_npi = df_target.loc[target_idx_to_update, TARGET_NPI_COL] if TARGET_NPI_COL in df_target.columns else "N/A"


                # Perform the update
                df_target.loc[target_idx_to_update, TARGET_FIRST_NAME_COL] = truth_first
                df_target.loc[target_idx_to_update, TARGET_LAST_NAME_COL] = truth_last
                df_target.loc[target_idx_to_update, TARGET_FULL_NAME_COL] = f"{truth_first} {truth_last}".strip() # Reconstruct full name
                
                updates_log.append(
                    f"  - Updated Target Index {target_idx_to_update} (NPI: {original_target_npi}):\\n"
                    f"    FROM: '{original_target_first}' '{original_target_last}' ('{original_target_full}') \\n"
                    f"    TO  : '{truth_first}' '{truth_last}' (Matched '{truth_normalized_name}' with '{matched_name_in_target_list}', Score: {score})\\n"
                )
                updated_target_indices.add(target_idx_to_update)
            else:
                # All possible matches for this truth_name were already updated by other truth_names
                ambiguous_matches.append({
                    "truth_name": f"{truth_first} {truth_last}",
                    "matched_target_normalized_name": matched_name_in_target_list,
                    "score": score,
                    "target_indices": possible_target_indices,
                    "reason": "All potential target matches already claimed by prior updates."
                })
        else:
            unmatched_truth_providers.append({
                "truth_name": f"{truth_first} {truth_last} (Normalized: {truth_normalized_name})",
                "reason": f"No match found above threshold {MATCH_THRESHOLD}"
            })

    report_content.append("\\n--- Update Summary ---\\n")
    report_content.append(f"Total providers in truth file ('{os.path.basename(TRUTH_FILE_PATH)}'): {len(df_truth)}\\n")
    report_content.append(f"Total providers in target file ('{os.path.basename(TARGET_FILE_PATH)}'): {len(df_target)}\\n")
    report_content.append(f"Number of providers updated in target file: {len(updated_target_indices)}\\n")
    report_content.append(f"Number of truth providers not matched or not updated in target: {len(unmatched_truth_providers) + len(ambiguous_matches)}\\n")

    if updates_log:
        report_content.append("\\n--- Detailed Updates Log ---\\n")
        report_content.extend(updates_log)

    if unmatched_truth_providers:
        report_content.append("\\n--- Truth Providers Not Matched/Updated in Target File ---\\n")
        for item in unmatched_truth_providers:
            report_content.append(f"  - Truth Name: {item['truth_name']}\\n    Reason: {item['reason']}\\n")
            
    if ambiguous_matches:
        report_content.append("\\n--- Ambiguous/Skipped Matches (Truth providers where targets were already claimed) ---\\n")
        for item in ambiguous_matches:
            report_content.append(f"  - Truth Name: {item['truth_name']}\\n    Attempted to match with target normalized name: '{item['matched_target_normalized_name']}' (Score: {item['score']})\\n    Potential Target Indices: {item['target_indices']}\\n    Reason: {item['reason']}\\n")


    target_providers_not_updated = df_target[~df_target.index.isin(updated_target_indices)]
    report_content.append(f"\\nNumber of providers in target file *not* updated: {len(target_providers_not_updated)}\\n")
    if not target_providers_not_updated.empty:
        report_content.append("  (These are providers in the original target file that had no corresponding match from the truth file or were not chosen for an update)\\n")
        # Optionally list some of them:
        # report_content.append("\\n--- Target Providers Not Updated (Sample) ---\\n")
        # for idx_target, row_target in target_providers_not_updated.head().iterrows():
        #     npi = row_target[TARGET_NPI_COL] if TARGET_NPI_COL in df_target.columns else "N/A"
        #     report_content.append(f"  - Index: {idx_target}, Name: {row_target[TARGET_FIRST_NAME_COL]} {row_target[TARGET_LAST_NAME_COL]}, NPI: {npi}\\n")


    # Save the updated DataFrame
    try:
        # Make sure the output directory exists
        os.makedirs(os.path.dirname(OUTPUT_TARGET_FILE_PATH), exist_ok=True)
        df_target.drop(columns=['Normalized_Name_Target'], inplace=True, errors='ignore') # Clean up helper column
        df_target.to_csv(OUTPUT_TARGET_FILE_PATH, index=False)
        report_content.append(f"\\nSuccessfully saved updated target file to: {OUTPUT_TARGET_FILE_PATH}\\n")
        print(f"Updated target file saved to: {OUTPUT_TARGET_FILE_PATH}")
    except Exception as e:
        report_content.append(f"\\nERROR: Could not save updated target file. Error: {e}\\n")
        print(f"ERROR: Could not save updated target file. Error: {e}")

    # Save the report
    try:
        os.makedirs(os.path.dirname(REPORT_FILE_PATH), exist_ok=True)
        with open(REPORT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("".join(report_content).replace("\\\\n", "\\n")) # Ensure newlines are correctly written
        print(f"Standardization report saved to: {REPORT_FILE_PATH}")
    except Exception as e:
        print(f"ERROR: Could not save report file. Error: {e}")

if __name__ == "__main__":
    main() 