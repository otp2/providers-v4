import pandas as pd
import os

# Define file paths
input_file = os.path.join('01_working_data_transformation', '00_working_data_transformation', 'working_pulse_v3.csv')
output_file = os.path.join('01_working_data_transformation', '00_working_data_transformation', 'working_pulse_v4.csv')

# Read the CSV file
print(f"Reading input file from: {input_file}")
df = pd.read_csv(input_file)

# Merge Clinical Interests into Specialties column
print("Merging Clinical Interests into Specialties column...")
for index, row in df.iterrows():
    # Check if both columns have values
    if pd.notna(row['Clinical Interests']) and pd.notna(row['Specialties']):
        # Add Clinical Interests to end of Specialties
        df.at[index, 'Specialties'] = f"{row['Specialties']},{row['Clinical Interests']}"
    # If only Clinical Interests has value but Specialties is empty
    elif pd.notna(row['Clinical Interests']) and pd.isna(row['Specialties']):
        df.at[index, 'Specialties'] = row['Clinical Interests']
    # Otherwise keep Specialties as is

# Remove the Care Philosophy and My Endeavor Statement columns
print("Removing Care Philosophy and My Endeavor Statement columns...")
df = df.drop(columns=['Care Philosophy', 'My Endeavor Statement'], errors='ignore')

# Save the modified data to a new CSV file
print(f"Saving output to: {output_file}")
df.to_csv(output_file, index=False)

print("Transformation complete. Created working_pulse_v4.csv") 