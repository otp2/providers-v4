import pandas as pd
import os

# Define file paths
source_file = "00_source_data/00_original_providers_all_providers/providers_all_providers_name_standardized.csv"
target_file = "02_combination/04_all_providers/all_providers.csv"
output_file = "02_combination/04_all_providers/all_providers_with_emails.csv"

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Read the source CSV that contains email addresses
print(f"Reading source file: {source_file}")
source_df = pd.read_csv(source_file)
print(f"Source file contains {len(source_df)} rows")

# Create a dictionary mapping NPI to email address
email_map = dict(zip(source_df['National Provider Identifier (NPI)'], source_df['Email Address']))
print(f"Created email mapping for {len(email_map)} providers")

# Read the target CSV file where we want to add email addresses
print(f"Reading target file: {target_file}")
target_df = pd.read_csv(target_file)
print(f"Target file contains {len(target_df)} rows")

# Create a new column 'Email' in the target dataframe
# Map email addresses from source to target by matching NPIs
target_df['Email'] = target_df['NPI'].map(email_map)

# Print some stats about the mapping
mapped_count = target_df['Email'].notna().sum()
print(f"Successfully mapped {mapped_count} email addresses")
print(f"Could not map {len(target_df) - mapped_count} email addresses")

# Save the updated dataframe to a new CSV file
print(f"Saving updated file to: {output_file}")
target_df.to_csv(output_file, index=False)
print("Done!") 