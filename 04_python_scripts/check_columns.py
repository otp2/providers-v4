import pandas as pd

# Load the CSV file
file_path = '01_working_data_transformation/00_working_data_transformation/working_pulse_v5.csv'
df = pd.read_csv(file_path)

# Print column names
print("Columns in working_pulse_v5.csv:")
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

# Confirm Clinical Interests is not in the columns
if 'Clinical Interests' in df.columns:
    print("\nWarning: 'Clinical Interests' column is still present!")
else:
    print("\nConfirmed: 'Clinical Interests' column has been removed.") 