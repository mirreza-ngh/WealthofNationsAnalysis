# Wealth of Nations — Data Analysis Project

## Overview
This project explores how economic prosperity relates to population well-being using data from the **World Bank Open Data API**.

We analyze the relationships between:
- GDP per capita (current US$)
- Life expectancy at birth
- Health spending per capita
- Under-5 child mortality

The goal is to reveal trends and correlations that explain how nations thrive.

## Project Structure
wealth-of-nations/
├── README.md # Project overview
├── requirements.txt # Dependencies
├── .gitignore # Ignored files (Python)
├── won/ # Source package
│ ├── init.py
│ ├── config.py # Indicator codes and constants
│ ├── data.py # Fetches World Bank data
│ ├── transform.py # Cleans and merges data
│ └── viz.py # Generates plots
├── presentation/
│ └── wealth_of_nations.ipynb # Jupyter notebook for analysis
└── tests/
└── test_data.py # Basic automated tests
