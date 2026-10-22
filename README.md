# Road Accident Prediction System

A Python desktop application for analyzing historical Delhi road-crash data, visualizing accident trends, and estimating annual crashes and fatalities using Linear Regression.

## Project Purpose

- Analyze historical road accident data and identify trends.
- Estimate annual road crashes, road-crash fatalities, and fatal road crashes for a selected year.
- Present data and results through charts and a desktop interface.
- Support learning and exploratory road-safety analysis.

> **Important:** Predictions are estimates based on historical data and are intended for educational and exploratory use. They should not be used as the sole basis for real-world road-safety or emergency decisions.

## Features

- Read and explore road-crash data from Excel.
- Clean and prepare data for analysis.
- Estimate yearly accident-related values using Scikit-learn Linear Regression.
- Visualize historical data and estimates with Matplotlib.
- Provide a desktop interface using Tkinter.
- Evaluate model performance with MAE, RMSE, and R² where applicable.

## Technology Stack

- **Python**
- **Pandas** — data handling and preparation
- **NumPy** — numerical operations
- **Matplotlib** — charts and visualizations
- **Scikit-learn** — Linear Regression and model evaluation
- **Tkinter** — desktop graphical user interface
- **Excel / openpyxl** — workbook data

## Project Structure

```text
RoadCrash/
├── data_cleaniness.py
├── Road_Accident_Prediction(2).py
├── Road_Crashes_Data(4).xlsx
└── README.md
```

Update the filenames above if you have renamed files in your repository.

## Requirements

- Python 3.10 or later recommended
- pip
- The project Excel dataset
- The libraries listed below

## Installation and Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Shdeep2917/RoadCrash.git
   cd RoadCrash
   ```

2. **Create and activate a virtual environment (recommended)**

   Windows:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   macOS/Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install pandas numpy matplotlib scikit-learn openpyxl
   ```

   Tkinter is commonly included with standard Python installations. Some Linux distributions require a separate Tkinter package.

## How to Run

Run the data-cleaning script first if it prepares the workbook used by the application:

```bash
python data_cleaniness.py
```

Then launch the application:

```bash
python "Road_Accident_Prediction(2).py"
```

Use the actual filenames in your repository if they differ. If the application expects the Excel file in a specific location, keep the workbook there or update the file path in the code.

## How It Works

1. Reads historical road-crash data from Excel.
2. Prepares the data for analysis.
3. Uses year as the model input to estimate annual accident-related values.
4. Displays results and visualizations in the desktop interface.
5. Reports evaluation metrics when suitable data is available.

## Model and Evaluation

The project uses **Linear Regression** to estimate yearly values. Evaluation may include:

- **MAE (Mean Absolute Error):** average absolute difference between actual and estimated values.
- **RMSE (Root Mean Squared Error):** gives greater weight to larger errors.
- **R² (Coefficient of Determination):** indicates how well the model explains variation in the evaluation data.

Metric values depend on the dataset and evaluation method; they do not guarantee future accuracy.

## Limitations

- Estimates depend on the quality, coverage, and consistency of the historical dataset.
- The model uses year as its input, so it does not account for weather, traffic volume, road conditions, vehicle type, or driver behaviour unless those features are added.
- Historical trends may not continue in the future.
- This is a learning and exploratory project, not a production road-safety forecasting service.

## Future Improvements

- Add features such as weather, traffic volume, road conditions, and time of day.
- Compare Linear Regression with other suitable machine-learning models.
- Improve validation with time-based train/test splits.
- Add filters for year, location, crash type, and severity.
- Improve validation and handling of missing or inconsistent values.
- Add clearer model-performance reports and prediction uncertainty ranges.

## Repository

GitHub: https://github.com/Shdeep2917/RoadCrash

## Author

**Deepak Kumar**

## License

No license is specified in this README. Add a `LICENSE` file if you want to publish the project under a particular open-source license.
