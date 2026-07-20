## NOAA Climate Data Pipeline

### 📌 Project Overview
This repository contains the data pipeline that feeds the climate dashboard page located here: https://climatebecky.com/cag_dashboard. It has been decoupled from the repository containing the front-end application to separate the data extraction and processing from the user interface.

The pipeline fetches official raw climate datasets from NOAA NCEI's nClimDiv (ClimDiv) fixed-width text files, processes and cleans the data, compresses it into NetCDF and intermediate CSV files, and pushes a production-ready CSV master file to the dashboard repository.

See Climate Becky Website repository for the front-end user interface: https://github.com/beckybol/climate_dashboard

### 🚀 Pipeline Workflow

1. **Extract**: Downloads state and county fixed-width text files directly from the NOAA NCEI climdiv backend directory using official processing release dates (procdate.txt). This data updates once per month.

2. **Transform**: Cleans the data, aligns time-series indices, handles missing values, strips un-occurred trailing future months for current-year files, and structures it using pandas and xarray.

3. **Archive**: Generates a NetCDF (.nc) file for long-term, compressed local storage.

4. **Load (Handoff)**: Uses environment variables to automatically detect the local dashboard repository and push the final master_climate_data.csv directly into its data/ directory.

### 📂 Repository Structure

```python
cag_data_pipeline/
├── fetch_climdiv_data.py  # Main script to fetch, parse, and archive NOAA climdiv text files
├── data_structure.py      # ETL script to format, filter, and push final CSV master file
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

#### Fetch and Parse Data
Run the extraction script to download the latest NOAA fixed-width text files, parse state and county datasets, compress them into NetCDF files, and output intermediate wide-format CSVs:

```bash
python fetch_climdiv_data.py
```

#### Structure and Push Master Data
Once the extraction script has finished and intermediate data is available, execute the structuring script to generate and push the master file:

```bash
python data_structure.py
```

If successful, the script will output confirmation that the master data file was saved locally and successfully pushed to the target dashboard directory.

