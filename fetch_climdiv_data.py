import os
import requests
import pandas as pd
import xarray as xr
from datetime import datetime
import shutil

# Configuration
BASE_URL = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/"
VARIABLES = ["tmpc", "tmax", "tmin", "pcpn"]
DATA_DIR = os.path.join(os.getcwd(), 'data')
ARCHIVE_DIR = os.path.join(os.getcwd(), 'archive')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Standard requests header to prevent connection drops
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_procdate():
    """Fetches the current processing date from NCEI."""
    print("Fetching procdate.txt...")
    response = requests.get(f"{BASE_URL}procdate.txt", headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text.strip()

def download_climdiv_file(filename):
    """Downloads a file from the climdiv directory if it doesn't already exist locally."""
    local_path = os.path.join(DATA_DIR, filename)
    url = f"{BASE_URL}{filename}"
    
    # ADD THIS CHECK: If the file is already there, skip the download
    if os.path.exists(local_path):
        print(f"File {filename} already exists locally. Skipping download.")
        return local_path
        
    print(f"Downloading {filename}...")
    response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
    response.raise_for_status()
    
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return local_path

def parse_fixed_width_climdiv(filepath, level='state'):
    """
    Parses the NCEI fixed-width text files.
    State IDs are 10 characters; County IDs are 11 characters.
    """
    # For file structure, see readme files in the parent directory of the data:
    # https://www.ncei.noaa.gov/pub/data/cirs/climdiv/state-readme.txt
    # https://www.ncei.noaa.gov/pub/data/cirs/climdiv/county-readme.txt
    
    # 1. Dynamically set column widths based on file level
    if level == 'state':
        col_widths = [10] + [7] * 12
    elif level == 'county':
        col_widths = [11] + [7] * 12
        
    col_names = ['ID'] + [f'{i:02d}' for i in range(1, 13)]
    
    # 2. Read the file, explicitly forcing the ID column to be a string
    df = pd.read_fwf(filepath, widths=col_widths, names=col_names, header=None, dtype={'ID': str})
    
    # 3. Slice the string based on the correct index lengths
    if level == 'state':
        df['State_Code'] = df['ID'].str[0:3]
        df['Year'] = df['ID'].str[6:10] # Year is at the end of the 10-char string
    elif level == 'county':
        df['State_FIPS'] = df['ID'].str[0:2]
        df['County_FIPS'] = df['ID'].str[2:5]
        df['Year'] = df['ID'].str[7:11] # Year is at the end of the 11-char string

    # Melt the dataframe from wide (12 month columns) to long (one value column)
    id_vars = ['ID', 'Year', 'State_Code'] if level == 'state' else ['ID', 'Year', 'State_FIPS', 'County_FIPS']
    df_long = df.melt(id_vars=id_vars, value_vars=[f'{i:02d}' for i in range(1, 13)], 
                      var_name='Month', value_name='Value')
    
    # Create a proper datetime index
    df_long['Date'] = pd.to_datetime(df_long['Year'] + df_long['Month'] + '01', format='%Y%m%d')
    df_long = df_long.set_index('Date').sort_index()
    
    # Clean missing data flags (-9.99 or -99.90 usually)
    df_long.loc[df_long['Value'] < -9.0, 'Value'] = float('nan')
    
    return df_long

def create_netcdf(state_df, county_df, procdate):
    """Converts the pandas DataFrames to clean xarray Datasets and saves as NetCDF efficiently."""
    print("Converting to NetCDF...")
    
    # 1. Process State Dataset
    state_pivot = state_df.reset_index().pivot_table(
        index='Date', columns=['State_Code', 'Variable'], values='Value'
    )
    state_pivot.columns = [f"{col[0]}_{col[1]}" for col in state_pivot.columns]
    ds_state = xr.Dataset.from_dataframe(state_pivot)
    
    # 2. Process County Dataset
    county_df['County_ID'] = county_df['State_FIPS'] + county_df['County_FIPS']
    county_pivot = county_df.reset_index().pivot_table(
        index='Date', columns=['County_ID', 'Variable'], values='Value'
    )
    county_pivot.columns = [f"{col[0]}_{col[1]}" for col in county_pivot.columns]
    ds_county = xr.Dataset.from_dataframe(county_pivot)
    
    # Set output paths
    state_nc_path = os.path.join(DATA_DIR, 'statewide_climate_data.nc')
    county_nc_path = os.path.join(DATA_DIR, 'county_climate_data.nc')
    
    # Save with compression enabled (Zlib)
    encoding = {var: {'zlib': True, 'complevel': 4} for var in ds_state.data_vars}
    ds_state.to_netcdf(state_nc_path, encoding=encoding)
    
    encoding_county = {var: {'zlib': True, 'complevel': 4} for var in ds_county.data_vars}
    ds_county.to_netcdf(county_nc_path, encoding=encoding_county)
    
    print(f"Saved optimized NetCDF files to {DATA_DIR}")
    
    # Archive logic using the official procdate
    shutil.copy2(state_nc_path, os.path.join(ARCHIVE_DIR, f"statewide_climate_data_{procdate}.nc"))
    shutil.copy2(county_nc_path, os.path.join(ARCHIVE_DIR, f"county_climate_data_{procdate}.nc"))
    print(f"Archived copies saved to {ARCHIVE_DIR} with procdate: {procdate}")

def main():
    try:
        procdate = get_procdate()
        print(f"Latest procdate: {procdate}")
        
        all_state_data = []
        all_county_data = []

        for var in VARIABLES:
            # Construct filenames based on NCEI naming conventions
            state_file = f"climdiv-{var}st-v1.0.0-{procdate}"
            county_file = f"climdiv-{var}cy-v1.0.0-{procdate}"
            
            # Download files
            state_path = download_climdiv_file(state_file)
            county_path = download_climdiv_file(county_file)
            
            # Parse files
            print(f"Parsing {var} data...")
            state_df = parse_fixed_width_climdiv(state_path, level='state')
            state_df['Variable'] = var
            all_state_data.append(state_df)
            
            county_df = parse_fixed_width_climdiv(county_path, level='county')
            county_df['Variable'] = var
            all_county_data.append(county_df)

        # Combine variables
        final_state_df = pd.concat(all_state_data)
        final_county_df = pd.concat(all_county_data)
        
        # Save to NetCDF
        create_netcdf(final_state_df, final_county_df, procdate)

        # Output raw CSVs for the data_structure.py script to pick up
        print("Exporting intermediate wide-format CSVs for data_structure.py...")
        for var in VARIABLES:
            var_df = final_state_df[final_state_df['Variable'] == var].reset_index()
            
            # We need to map state codes back to state names to match states.py or your original columns
            # Let's import state_dict to pivot using full state names
            from states import state_dict
            
            # Create a reverse lookup or map state codes if needed. 
            # Alternatively, if your dataframe has State_Code, let's pivot on that or full names.
            # Let's pivot using State_Code or map to names:
            # (Assuming state_df has 'State_Code' like '001', let's map them or pivot by state name)
            
            # Quick pivot: index='Date', columns='State_Code' (or name), values='Value'
            pivoted = var_df.pivot(index='Date', columns='State_Code', values='Value')
            
            # Map state number strings ('001') back to state names ('Alabama') if your states.py uses numeric keys
            # Let's convert column names from string codes ('001') to integers (1) to match state_dict
            pivoted.columns = [int(c) for c in pivoted.columns]
            pivoted = pivoted.rename(columns=state_dict)
            
            # Reset index so 'Date' becomes a column named 'time' to match your original pipeline expectation
            pivoted = pivoted.reset_index().rename(columns={'Date': 'time'})
            
            name_map = {'tmpc': 'tavg', 'tmax': 'tmax', 'tmin': 'tmin', 'pcpn': 'pcp'}
            csv_path = os.path.join(DATA_DIR, f"cag_{name_map[var]}_data.csv")
            pivoted.to_csv(csv_path, index=False)

        print("Data extraction complete! You can now run data_structure.py")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()