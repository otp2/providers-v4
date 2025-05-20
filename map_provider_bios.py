import pandas as pd
import os

# Define file paths
source_file = "00_source_data/00_original_providers_all_providers/providers_all_providers_name_standardized.csv"
target_file = "02_combination/04_all_providers/all_providers_with_emails.csv"
output_file = "02_combination/04_all_providers/all_providers_with_emails_bios.csv"

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Read the source CSV that contains bios
print(f"Reading source file: {source_file}")
source_df = pd.read_csv(source_file)
print(f"Source file contains {len(source_df)} rows")

# Create dictionaries mapping NPI to bio
bio_map = dict(zip(source_df['National Provider Identifier (NPI)'], source_df['Bio - Legacy Sites']))
print(f"Created bio mapping for {len(bio_map)} providers")

# Read the target CSV file where we want to add bios
print(f"Reading target file: {target_file}")
target_df = pd.read_csv(target_file)
print(f"Target file contains {len(target_df)} rows")

# Map bios from source to target by matching NPIs
target_df['Legacy Bio'] = target_df['NPI'].map(bio_map)

# Print some stats about the mapping
mapped_count = target_df['Legacy Bio'].notna().sum()
print(f"Successfully mapped {mapped_count} legacy bios")
print(f"Could not map {len(target_df) - mapped_count} legacy bios")

# Save the updated dataframe to a new CSV file
print(f"Saving updated file to: {output_file}")
target_df.to_csv(output_file, index=False)
print("Done!") 