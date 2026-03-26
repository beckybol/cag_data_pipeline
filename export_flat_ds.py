## This file reads the dataset created in get_cag_data.ipynb
## and exports CSV files for tavg, tmin, tmax, and pcp variables
## Becky Bolinger, January 2026

import pandas as pd
import os
import xarray as xr
from states import ordered_state_names

def export_csvs_from_ds(ds, output_dir='.'):
    """
    Exports CSV files for tavg, tmin, tmax, and pcp from a Dataset 
    where variables are named in the format '{State}_{Variable}'.
    """
    # The four variable types we want to extract
    var_types = ['tavg', 'tmin', 'tmax', 'pcp']
    
    for var_type in var_types:
        print(f"Exporting {var_type} data...")
        
        # Find all variables in the dataset that end with this suffix
        # Example: 'Alabama_tavg' matches 'tavg'
        matching_vars = [v for v in ds.data_vars if str(v).endswith(f"_{var_type}")]
        
        if not matching_vars:
            print(f"  No variables found for {var_type}")
            continue
            
        # Collect data into a dictionary: {State_Name: Series}
        state_data = {}
        for var_name in matching_vars:
            # Extract the state name.
            # Try to get it from attributes first
            state_name = ds[var_name].attrs['state']

            # Convert the DataArray to a pandas Series
            # This assumes the DataArray has a 'time' dimension which becomes the index
            state_data[state_name] = ds[var_name].to_series()
            
        # Create a DataFrame from the dictionary
        # Pandas automatically aligns the time indices
        df = pd.DataFrame(state_data)
        
        # Sort columns (states) according to the custom order (Alaska 50, Hawaii 51)
        cols = [s for s in ordered_state_names if s in df.columns]
        extra_cols = [c for c in df.columns if c not in cols]
        df = df[cols + sorted(extra_cols)]
        
        # Define output filename
        output_filename = f"cag_{var_type}_data.csv"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save to CSV
        df.to_csv(output_path)
        print(f"  Saved to {output_path}")

if __name__ == "__main__":
    print("This script defines the function 'export_csvs_from_ds(ds)'.")
    print("You can import it and use it with your in-memory Dataset:")
    print("  from export_flat_ds import export_csvs_from_ds")
    print("  export_csvs_from_ds(ds)")