# Sales Performance Analysis & Predictive Sales Forecasting

## Project Overview
This project analyses retail sales data to identify business trends, evaluate sales and profitability, and predict monthly sales using Python, SQL Server, and Power BI.

## Objectives
- Analyse overall sales, profit, and quantity.
- Identify top-performing products and categories.
- Compare sales performance across regions and customer segments.
- Study monthly and yearly sales trends.
- Build a machine learning model for monthly sales forecasting.
- Present business insights through an interactive Power BI dashboard.

## Technologies Used
- **Python:** Data cleaning, analysis, feature engineering, and forecasting.
- **SQL Server:** Data storage, validation, and business analysis.
- **Power BI:** Interactive dashboard and visualisation.
- **Libraries:** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn, Joblib, PyODBC.

## Dataset
Sample Superstore dataset containing retail transaction information, including:
- Orders and customers
- Products and categories
- Sales and profit
- Quantity and discounts
- Regions and shipping details

## Project Structure

```text
Sales_Performance_Analysis/
│
├── Dataset/
├── SQL/
│   └── Sales_Analysis.sql
├── Python/
│   └── sales_analysis.py
├── POWERBI/
│   └── Sales_Performance_Dashboard.pbix
├── Models/
│   ├── linear_regression_model.pkl
│   ├── random_forest_model.pkl
│   ├── monthly_sales_forecast_model.pkl
│   ├── monthly_forecast_features.pkl
│   └── model_features.pkl
├── Outputs/
│   ├── monthly_sales_predictions.csv
│   └── actual_vs_predicted_sales.png
├── DOCUMENTATION/
└── README.md
```

## SQL Analysis
SQL queries were used for:
- Data validation and quality checks
- Overall business KPIs
- Category and sub-category analysis
- Regional and customer performance
- Monthly and yearly sales trends
- Discount and shipping analysis
- Ranking and running total calculations

## Python Analysis
Python was used for:
- Data cleaning and preprocessing
- Exploratory data analysis
- Feature engineering
- Data visualisation
- Machine learning model development
- Monthly sales forecasting

## Power BI Dashboard
The interactive dashboard includes:
- Total Sales
- Total Orders
- Total Profit
- Total Quantity
- Sales by Category
- Profit by Region
- Sales by Segment
- Sales by State
- Top 10 Products by Sales
- Monthly Sales Trends

Interactive slicers allow users to explore the data by year, region, and customer segment.

## Model Outputs
The project saves trained machine learning models and prediction results for further analysis.

## Key Business Metrics
- Total Records: 9,994
- Total Orders: 5,009
- Total Sales: Approximately $2.30 million
- Total Profit: Approximately $286.82 thousand
- Total Quantity: 37,873

## Author
Developed as a data analytics and machine learning portfolio project.