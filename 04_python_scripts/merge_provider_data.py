import pandas as pd
import os

# Define file paths
source_providers_file = os.path.join('00_source_data', '00_original_providers_all_providers', 'providers_all_providers_name_standardized.csv')
working_pulse_file = os.path.join('01_working_data_transformation', '00_working_data_transformation', 'working_pulse_v2.csv')
output_file = os.path.join('01_working_data_transformation', '00_working_data_transformation', 'working_pulse_v3.csv')

# Read the CSV files
print(f"Reading source providers file from: {source_providers_file}")
providers_df = pd.read_csv(source_providers_file)
print(f"Reading working pulse file from: {working_pulse_file}")
pulse_df = pd.read_csv(working_pulse_file)

# Define field mappings
field_mappings = {
    'Profile Link - Legacy Site': 'Website',
    'Bio - Legacy Sites': 'Bio',
    'Care Philosophy': 'Care Philosophy',
    'My Endeavor Statement': 'My Endeavor Statement',
    'Pronouns': 'Pronouns',
    'Languages': 'Languages',
    'Clinical Interests - Legacy Sites': 'Clinical Interests',
    'Psychiatrist - Education (Med School)': 'Psychiatrist - Education',
    'Psychiatrist - Year Graduated (Med School)': 'Psychiatrist - Year Graduated',
    'Therapist - Education': 'Therapist - Education',
    'Therapist - Year Graduated': 'Therapist - Year Graduated',
    'Residency': 'Residency',
    'Residency - Year Completed': 'Residency - Year Completed',
    'Fellowship': 'Fellowship',
    'Fellowship - Year Completed': 'Fellowship - Year Completed',
    'Board Certification - Name': 'Board Certification - Name',
    'Board Certification - Year Received': 'Board Certification - Year Received',
    'Awards and Honors': 'Awards and Honors',
    'Professional Titles': 'Professional Titles'
}

# Merge the dataframes on NPI
print("Merging data based on NPI...")
merged_df = pulse_df.copy()

# Add the fields from providers_df based on the field mappings
for original_field, new_field_name in field_mappings.items():
    # Create a dictionary mapping NPI to the field value
    if original_field in providers_df.columns:
        field_dict = dict(zip(providers_df['National Provider Identifier (NPI)'], providers_df[original_field]))
        
        # Add the field to the merged dataframe
        merged_df[new_field_name] = merged_df['NPI'].map(field_dict)
        print(f"Added field: {new_field_name}")
    else:
        print(f"Warning: Field '{original_field}' not found in providers file")

# Save the merged dataframe
print(f"Saving merged data to: {output_file}")
merged_df.to_csv(output_file, index=False)

print("Data merge completed successfully!")
print(f"Original pulse records: {len(pulse_df)}")
print(f"Merged pulse records: {len(merged_df)}")
print(f"New fields added: {len(field_mappings)}") 