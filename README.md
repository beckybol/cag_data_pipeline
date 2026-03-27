## NOAA Climate Data Pipeline

### 📌 Project Overview
This repository contains the data pipeline that feeds the climate dashboard page located here: https://climatebecky.com/cag_dashboard. It has been decoupled from the repository containing the front-end application to separate the data extraction and processing from the user interface.

The pipeline fetches raw climate data from NOAA NCEI's Climate at a Glance tool, processes the data, writes it to netcdf and CSV files, and pushes a production-ready CSV master file to the dashboard repository.

See Climate Becky Website repository for the front-end user interface: https://github.com/beckybol/climate_dashboard

### 🚀 Pipeline Workflow

1. **Extract**: Retrieves the latest temperature and precipitation data via the NOAA NCEI Climate at a Glance tool (https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/). This data updates once per month.

2. **Transform**: Cleans the data, aligns time-series indices, and structures it for dashboard consumption using pandas and xarray.

3. **Archive**: Generates a NetCDF (.nc) file for long-term, compressed local storage.

4. **Load (Handoff)**: Uses environment variables to automatically detect the local dashboard repository and push the final master_climate_data.csv directly into its data/ directory.

### 📂 Repository Structure

```python
climate_data_pipeline/
├── get_statewide_cag_data.ipynb  # Notebook for initial data extraction and processing
├── data_structure.py      # Main ETL script to format and push final CSV
├── export_flat_ds.py      # Helper functions for dataset manipulation
├── states.py              # Helper function for indexing the states
├── .env.example           # Template for local path configuration
├── requirements.txt       # Python dependencies
└── .gitignore             # Keeps raw data and private .env files out of version control
```

### ⚙️ Local Setup & Configuration

1. Clone the repository:

```bash
git clone https://github.com/beckybol/cag_data_pipeline.git
```

2. Set up the virtual environment:

It is recommended to run this pipeline in an isolated environment.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure the dashboard handoff

To allow this pipeline to push data directly to your local dashboard without hardcoding paths, you must set up your local environment file.

Copy the example environment file:  
```cp .env.example .env``` (or manually duplicate and rename the file).

Open .env and update the DASHBOARD_DATA_PATH variable to point to the data/ directory inside your cloned dashboard repository:

```
# Example inside your new .env file
DASHBOARD_DATA_PATH=/Users/YourName/git_projects/climate_dashboard/data
```

### Running the Code
Once configured, you are ready to grab the data!

#### get_statewide_cag_data.ipynb
The first cell in the notebook grabs the temperature and precipitation data for all months and every state. These data are placed in 4 separate CSV files, one for each variable in a data directory. A NetCDF file is also created with all of the data, and is also placed in the data directory. **The first cell must be run to create the local data files!**

The second cell can be run to archive the NetCDF file. This will create an archive directory, and add a timestamp to the filename. This is not a necessary step, but may be desirable to have as a backup.

The third cell provides an example of reading the NetCDF file. It is also not necessary to run this cell.

#### data_structure.py
Once the first cell of the notebook has been run in the previous step, and data are available, execute the following command:

```bash
python data_structure.py
```

If successful, the script will output confirmation that the master data file was saved locally and successfully pushed to the target dashboard directory.

