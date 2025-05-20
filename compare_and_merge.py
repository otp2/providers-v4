import pandas as pd
import os

# Define file paths
file1 = "02_combination/00_in_progress/combined_providers_v2.csv"
file2 = "02_combination/03_not_in_pulse_or_guidebook/providers_not_in_pulse_or_guidebook_v3.csv"
output_dir = "02_combination/04_all_providers"
output_file = os.path.join(output_dir, "all_providers.csv")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the CSV files
df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Print column headers for comparison
print("Headers in combined_providers_v2.csv:")
print(df1.columns.tolist())
print("\nHeaders in providers_not_in_pulse_or_guidebook_v3.csv:")
print(df2.columns.tolist())

# Check if the headers are the same
headers_match = list(df1.columns) == list(df2.columns)
print(f"\nDo headers match? {headers_match}")

# If headers don't match, print differences
if not headers_match:
    print("\nColumns in file 1 but not in file 2:")
    print(set(df1.columns) - set(df2.columns))
    print("\nColumns in file 2 but not in file 1:")
    print(set(df2.columns) - set(df1.columns))

# Combine the data frames
combined_df = pd.concat([df1, df2], ignore_index=True)
print(f"\nCombined dataframe shape: {combined_df.shape}")

# Save the combined data to a new file
combined_df.to_csv(output_file, index=False)
print(f"Combined data saved to {output_file}") 