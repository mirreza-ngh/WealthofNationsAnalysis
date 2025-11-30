# Wealth of Nations — Data Analysis & Dashboard

This project provides a reproducible data workflow and an interactive dashboard for exploring global economic and health indicators. Data is sourced live from the **World Bank Open Data API**.

It includes:
- A **Jupyter Notebook** for exploratory analysis
- A **Streamlit app** for interactive visualization
- A modular Python package (`won/`) handling:
  - Data fetching
  - Cleaning and transformation
  - Plotting utilities
- Automated tests for data functionality


## Project Structure
```
.
├─ presentation/
│  └─ wealth_of_nations.ipynb   # Analysis logic
├─ won/                         # Python package
│  ├─ __init__.py
│  ├─ config.py                 # Indicator configuration
│  ├─ data.py                   # World Bank API interaction
│  ├─ transform.py              # Data transformation utilities
│  └─ viz.py                    # Matplotlib + Plotly visualizations
├─ app.py                       # Streamlit dashboard
├─ README.md
└─ requirements.txt
```
## Getting Started
### Clone the repository
```
git clone https://github.com/mirreza-ngh/WealthofNationsAnalysis.git
cd WealthofNationsAnalysis
```
### Create and activate a virtual environment (recommended)
```
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```
### Install dependencies
```
pip install -r requirements.txt
```

### Running the Dashboard
```
streamlit run app.py
```
This launches an interactive tool to explore:
- GDP per capita
- Life expectancy
- Health expenditure
- Child mortality
- Relationship plots and choropleth maps

### Using the Notebook
Launch Jupyter from the project root to ensure package imports work:
```
jupyter notebook
```
Then open:
```
presentation/wealth_of_nations.ipynb
```
The notebook demonstrates:
- Fetching multiple indicators
- Data cleaning/joining
- Correlation analysis
- Time series & scatter visualizations

## Data Source

#### World Bank Open Data API

All data is retrieved dynamically and may update over time.
