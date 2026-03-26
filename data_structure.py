import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

# Load the hidden environment variables
load_dotenv()

# Get the dashboard path from the .env file
# This will be where the final master_climate_data.csv is saved for the dashboard app
DASHBOARD_DIR_STRING = os.getenv("DASHBOARD_DATA_PATH")

# 1. Define file paths
files = {
    'Average Temperature': 'data/cag_tavg_data.csv',
    'Max Temperature': 'data/cag_tmax_data.csv',
    'Min Temperature': 'data/cag_tmin_data.csv',
    'Precipitation': 'data/cag_pcp_data.csv'
}

data_frames = []

# 2. Loop through files and standardize them
for variable_name, file_path in files.items():
    # Load the CSV
    # Assumption: The CSVs have columns like: 'Date', 'Alabama', 'Alaska', 'Arizona'...
    # If the first column is Date, we set index_col=0
    df = pd.read_csv(file_path)
    
    # 3. "Melt" the data from Wide to Long
    # This turns 50 state columns into one "State" column
    # id_vars should be your Date column. Change 'Date' if your column is named 'YearMonth' or similar.
    df_long = df.melt(id_vars=['time'], var_name='State', value_name='Value')
    
    # 4. Add a column identifying which variable this is (e.g., "Max Temp")
    df_long['Variable'] = variable_name
    
    # Append to our list
    data_frames.append(df_long)

# 5. Concatenate all 4 variables into one Master DataFrame
master_df = pd.concat(data_frames, ignore_index=True)

# 6. Data Cleanup & Helper Columns
# Convert Date column to actual datetime objects (critical for sorting/plotting)
master_df['Date'] = pd.to_datetime(master_df['time'], format='%Y-%m-%d') # Adjust format if needed

# Create the "Month" helper column for filtering requirement
master_df['Month'] = master_df['Date'].dt.month
master_df['Year'] = master_df['Date'].dt.year

# 7. (Optional) State ID Mapping
# Plotly maps often work best with 2-letter codes (AL, AK, etc.) rather than full names.
# We need a dictionary to map full names to abbreviations since CSVs use full names.
state_map = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Apply map only if your CSV has full names. If it already has codes, skip this.
master_df['State_Code'] = master_df['State'].map(state_map)

# 8. Check the output
print(master_df.head())
print(master_df.info())

# Save locally and to use in the dashboard app
local_data_dir = os.path.join(os.getcwd(), 'data')
local_output = os.path.join(local_data_dir, 'master_climate_data.csv')
master_df.to_csv(local_output, index=False)
print("Data processed and saved locally")

# 4. Push the data directly to the dashboard repository
if DASHBOARD_DIR_STRING:
    dashboard_path = Path(DASHBOARD_DIR_STRING)
    
    if dashboard_path.exists():
        final_target = dashboard_path / 'master_climate_data.csv'
        master_df.to_csv(final_target, index=False)
        print(f"Success: Pushed updated data to {final_target}")
    else:
        print("Warning: DASHBOARD_DATA_PATH found, but the directory does not exist.")
else:
    print("Notice: No DASHBOARD_DATA_PATH found in .env. Skipping dashboard update.")

