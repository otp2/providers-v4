import pandas as pd
import os

# Define file paths
input_file = os.path.join('01_working_data_transformation', '00_working_data_transformation', 'working_pulse_v4.csv')
output_file = os.path.join('01_working_data_transformation', '00_working_data_transformation', 'working_pulse_v5.csv')

# Read the CSV file
print(f"Reading input file from: {input_file}")
df = pd.read_csv(input_file)

# Remove the Clinical Interests column
print("Removing Clinical Interests column...")
df = df.drop(columns=['Clinical Interests'], errors='ignore')

# Save the modified data to a new CSV file
print(f"Saving output to: {output_file}")
df.to_csv(output_file, index=False)

print("Transformation complete. Created working_pulse_v5.csv") 