

import pyodbc
import pandas as pd
import os

os.makedirs("Models", exist_ok=True)
os.makedirs("Outputs", exist_ok=True)

# Connect to SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SIVA\\SQLEXPRESS;"
    "DATABASE=SalesAnalysisDB;"
    "Trusted_Connection=yes;"
)

print("SQL Server connected successfully!")

# Retrieve data
query = """
SELECT *
FROM dbo.SampleSuperstore;
"""

df = pd.read_sql(query, conn)


# =====================================
# DATA CLEANING
# =====================================

print("\nDATA CLEANING STARTED")

# 1. Check duplicate records
print("Duplicates before cleaning:", df.duplicated().sum())

# 2. Remove exact duplicate records
df.drop_duplicates(inplace=True)

# 3. Convert date columns
df["Order_Date"] = pd.to_datetime(
    df["Order_Date"], errors="coerce"
)

df["Ship_Date"] = pd.to_datetime(
    df["Ship_Date"], errors="coerce"
)

# 4. Check missing values
print("\nMissing values after cleaning:")
print(df.isnull().sum())

# 5. Check dataset dimensions
print("\nCleaned dataset shape:")
print(df.shape)

# 6. Check data types
print("\nUpdated data types:")
print(df.dtypes)

print("\nDATA CLEANING COMPLETED")

# =====================================
# FEATURE ENGINEERING
# =====================================

import numpy as np

print("\nFEATURE ENGINEERING STARTED")

# 1. Extract order year
df["Order_Year"] = df["Order_Date"].dt.year

# 2. Extract order month
df["Order_Month"] = df["Order_Date"].dt.month

# 3. Extract quarter
df["Order_Quarter"] = df["Order_Date"].dt.quarter

# 4. Extract day of week
df["Order_Day"] = df["Order_Date"].dt.dayofweek

# 5. Calculate shipping days
df["Shipping_Days"] = (
    df["Ship_Date"] - df["Order_Date"]
).dt.days

# 6. Calculate profit margin
df["Profit_Margin"] = np.where(
    df["Sales"] != 0,
    (df["Profit"] / df["Sales"]) * 100,
    np.nan
)

# 7. Calculate sales per unit
df["Sales_Per_Unit"] = np.where(
    df["Quantity"] != 0,
    df["Sales"] / df["Quantity"],
    np.nan
)

# 8. Create discount categories
df["Discount_Category"] = pd.cut(
    df["Discount"],
    bins=[-0.001, 0, 0.10, 0.20, 0.30, 1],
    labels=[
        "No Discount",
        "Low Discount",
        "Medium Discount",
        "High Discount",
        "Very High Discount"
    ]
)

print("\nNew Features Created:")
print(df[[
    "Order_Year",
    "Order_Month",
    "Order_Quarter",
    "Shipping_Days",
    "Profit_Margin",
    "Sales_Per_Unit",
    "Discount_Category"
]].head())

print("\nFEATURE ENGINEERING COMPLETED")

# =====================================
# MACHINE LEARNING DATA PREPARATION
# =====================================

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("\nMACHINE LEARNING STARTED")

# Select prediction features
features = [
    "Order_Year",
    "Order_Month",
    "Order_Quarter",
    "Order_Day",
    "Quantity",
    "Discount",
    "Shipping_Days"
]

target = "Sales"

# Create ML dataset
ml_df = df[features + [target]].copy()

# Remove rows with missing values in ML columns
ml_df = ml_df.dropna()

X = ml_df[features]
y = ml_df[target]

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("\nMACHINE LEARNING DATA PREPARATION COMPLETED")

# =====================================
# LINEAR REGRESSION MODEL
# =====================================

lr_model = LinearRegression()

lr_model.fit(X_train, y_train)

lr_predictions = lr_model.predict(X_test)

lr_mae = mean_absolute_error(y_test, lr_predictions)

lr_rmse = np.sqrt(
    mean_squared_error(y_test, lr_predictions)
)

lr_r2 = r2_score(y_test, lr_predictions)

print("\nLINEAR REGRESSION RESULTS")
print("MAE:", lr_mae)
print("RMSE:", lr_rmse)
print("R2 Score:", lr_r2)

# =====================================
# RANDOM FOREST MODEL
# =====================================

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_predictions = rf_model.predict(X_test)

rf_mae = mean_absolute_error(y_test, rf_predictions)

rf_rmse = np.sqrt(
    mean_squared_error(y_test, rf_predictions)
)

rf_r2 = r2_score(y_test, rf_predictions)

print("\nRANDOM FOREST RESULTS")
print("MAE:", rf_mae)
print("RMSE:", rf_rmse)
print("R2 Score:", rf_r2)


# =====================================
# MODEL COMPARISON
# =====================================

comparison = pd.DataFrame({
    "Model": ["Linear Regression", "Random Forest"],
    "MAE": [lr_mae, rf_mae],
    "RMSE": [lr_rmse, rf_rmse],
    "R2 Score": [lr_r2, rf_r2]
})

print("\nMODEL PERFORMANCE COMPARISON")
print(comparison)

best_model = (
    "Random Forest"
    if rf_rmse < lr_rmse
    else "Linear Regression"
)

print("\nBest model based on RMSE:", best_model)

# =====================================
# SAVE MACHINE LEARNING MODELS
# =====================================

import joblib
import os

# Create model folder
os.makedirs("Models", exist_ok=True)

# Save Linear Regression
joblib.dump(
    lr_model,
    "Models/linear_regression_model.pkl"
)

# Save Random Forest
joblib.dump(
    rf_model,
    "Models/random_forest_model.pkl"
)

# Save feature names
joblib.dump(
    features,
    "Models/model_features.pkl"
)

print("\nModels saved successfully!")

# ==========================================
# MONTHLY SALES FORECASTING
# ==========================================

# 1. Prepare monthly sales data
monthly_sales = (
    df.set_index("Order_Date")
      .resample("MS")["Sales"]
      .sum()
      .reset_index()
)

monthly_sales.columns = ["Month", "Sales"]

print("\nMonthly Sales Data:")
print(monthly_sales.head())


# 2. Create time-based features
monthly_sales["Year"] = monthly_sales["Month"].dt.year
monthly_sales["Month_Number"] = monthly_sales["Month"].dt.month
monthly_sales["Time_Index"] = range(len(monthly_sales))


# 3. Create lag features
monthly_sales["Lag_1"] = monthly_sales["Sales"].shift(1)
monthly_sales["Lag_2"] = monthly_sales["Sales"].shift(2)
monthly_sales["Lag_3"] = monthly_sales["Sales"].shift(3)


# 4. Remove rows with missing lag values
monthly_sales.dropna(inplace=True)

print("\nForecasting Dataset:")
print(monthly_sales.head())
print("Total monthly records:", len(monthly_sales))


# 5. Split data chronologically (80% training, 20% testing)
train_size = int(len(monthly_sales) * 0.8)

train_data = monthly_sales.iloc[:train_size]
test_data = monthly_sales.iloc[train_size:]


# 6. Select features and target
features = [
    "Year",
    "Month_Number",
    "Time_Index",
    "Lag_1",
    "Lag_2",
    "Lag_3"
]

X_train = train_data[features]
y_train = train_data["Sales"]

X_test = test_data[features]
y_test = test_data["Sales"]

print("\nTraining records:", len(train_data))
print("Testing records:", len(test_data))


# 7. Train Random Forest model
from sklearn.ensemble import RandomForestRegressor

forecast_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

forecast_model.fit(X_train, y_train)

print("\nSales forecasting model trained successfully!")


# 8. Predict sales for test period
y_pred = forecast_model.predict(X_test)

comparison = test_data[["Month", "Sales"]].copy()
comparison["Predicted_Sales"] = y_pred

print("\nActual vs Predicted Monthly Sales:")
print(comparison)
# Visualize actual vs predicted sales
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

plt.plot(
    comparison["Month"],
    comparison["Sales"],
    marker="o",
    label="Actual Sales"
)

plt.plot(
    comparison["Month"],
    comparison["Predicted_Sales"],
    marker="o",
    label="Predicted Sales"
)

plt.title("Actual vs Predicted Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("Outputs/actual_vs_predicted_sales.png")
plt.show()

print("\nForecast comparison chart saved!")

# 9. Evaluate forecasting performance
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\nForecasting Model Performance:")
print("Mean Absolute Error:", round(mae, 2))
print("Root Mean Squared Error:", round(rmse, 2))


# 10. Save forecasting model
import joblib
import os

os.makedirs("Models", exist_ok=True)

joblib.dump(
    forecast_model,
    "Models/monthly_sales_forecast_model.pkl"
)

joblib.dump(
    features,
    "Models/monthly_forecast_features.pkl"
)

print("\nMonthly forecasting model saved successfully!")


# 11. Save prediction results
os.makedirs("Outputs", exist_ok=True)

comparison.to_csv(
    "Outputs/monthly_sales_predictions.csv",
    index=False
)

print("\nPrediction results saved successfully!")


# Prepare monthly sales data
monthly_sales = (
    df.set_index("Order_Date")
      .resample("MS")["Sales"]
      .sum()
      .reset_index()
)

monthly_sales.columns = ["Month", "Sales"]

print("\nMonthly Sales Data:")
print(monthly_sales.head())
# Create time-based features
monthly_sales["Year"] = monthly_sales["Month"].dt.year
monthly_sales["Month_Number"] = monthly_sales["Month"].dt.month

monthly_sales["Time_Index"] = range(len(monthly_sales))

print("\nMonthly Sales with Time Features:")
print(monthly_sales.head())
# Create previous month sales features
monthly_sales["Lag_1"] = monthly_sales["Sales"].shift(1)
monthly_sales["Lag_2"] = monthly_sales["Sales"].shift(2)
monthly_sales["Lag_3"] = monthly_sales["Sales"].shift(3)

print("\nMonthly Sales with Lag Features:")
print(monthly_sales.head())
# Remove rows with missing lag values
monthly_sales.dropna(inplace=True)

print("\nForecasting Dataset:")
print(monthly_sales.head())

print("\nTotal monthly records:", len(monthly_sales))
# Split data chronologically
train_size = int(len(monthly_sales) * 0.8)

train_data = monthly_sales.iloc[:train_size]
test_data = monthly_sales.iloc[train_size:]

print("\nTraining records:", len(train_data))
print("Testing records:", len(test_data))
# Select input features and target
features = ["Year", "Month_Number", "Time_Index", "Lag_1", "Lag_2", "Lag_3"]

X_train = train_data[features]
y_train = train_data["Sales"]

X_test = test_data[features]
y_test = test_data["Sales"]

print("\nTraining and testing features prepared!")
print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
# Train Random Forest forecasting model
from sklearn.ensemble import RandomForestRegressor

forecast_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

forecast_model.fit(X_train, y_train)

print("\nSales forecasting model trained successfully!")
# Display first five records
print("\nFirst 5 records:")
print(df.head())

# Dataset dimensions
print("\nDataset dimensions:")
print(df.shape)

# Dataset information
print("\nDataset information:")
df.info()

# Missing values
print("\nMissing values:")
print(df.isnull().sum())

# =====================================
# EXPLORATORY DATA ANALYSIS
# =====================================

# 1. Dataset shape
print("\n1. Dataset Shape:")
print(df.shape)

# 2. First 5 records
print("\n2. First 5 Records:")
print(df.head())

# 3. Last 5 records
print("\n3. Last 5 Records:")
print(df.tail())

# 4. Column names
print("\n4. Column Names:")
print(df.columns.tolist())

# 5. Data types
print("\n5. Data Types:")
print(df.dtypes)

# 6. Dataset information
print("\n6. Dataset Information:")
df.info()

# 7. Statistical summary
print("\n7. Statistical Summary:")
print(df.describe())

# 8. Missing values
print("\n8. Missing Values:")
print(df.isnull().sum())

# 9. Duplicate records
print("\n9. Duplicate Records:")
print(df.duplicated().sum())

# 10. Overall sales and profit
print("\n10. Business Summary:")
print("Total Sales:", df["Sales"].sum())
print("Total Profit:", df["Profit"].sum())
print("Total Quantity:", df["Quantity"].sum())
print("Average Sales:", df["Sales"].mean())


import matplotlib.pyplot as plt
import seaborn as sns

# Set chart style
sns.set_theme(style="whitegrid")

# Convert Order_Date into datetime
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# =====================================
# 1. SALES BY CATEGORY
# =====================================

category_sales = df.groupby("Category")["Sales"].sum()

plt.figure(figsize=(8, 5))
category_sales.plot(kind="bar")
plt.title("Total Sales by Category")
plt.xlabel("Category")
plt.ylabel("Sales")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("sales_by_category.png")
plt.show()


# =====================================
# 2. PROFIT BY REGION
# =====================================

region_profit = df.groupby("Region")["Profit"].sum()

plt.figure(figsize=(8, 5))
region_profit.plot(kind="bar")
plt.title("Total Profit by Region")
plt.xlabel("Region")
plt.ylabel("Profit")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("profit_by_region.png")
plt.show()


# =====================================
# 3. MONTHLY SALES TREND
# =====================================

df["Year_Month"] = df["Order_Date"].dt.to_period("M")

monthly_sales = df.groupby("Year_Month")["Sales"].sum()

plt.figure(figsize=(12, 5))
monthly_sales.index = monthly_sales.index.astype(str)
monthly_sales.plot(kind="line", marker="o")

plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("monthly_sales_trend.png")
plt.show()


# =====================================
# 4. SALES DISTRIBUTION
# =====================================

plt.figure(figsize=(8, 5))
sns.histplot(df["Sales"], bins=40, kde=True)

plt.title("Sales Distribution")
plt.xlabel("Sales Amount")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("sales_distribution.png")
plt.show()


# =====================================
# 5. CORRELATION HEATMAP
# =====================================

numeric_columns = [
    "Sales",
    "Quantity",
    "Discount",
    "Profit"
]

plt.figure(figsize=(8, 5))

sns.heatmap(
    df[numeric_columns].corr(),
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Sales Data Correlation")
plt.tight_layout()
plt.savefig("correlation_heatmap.png")
plt.show()

print("All visualizations created successfully!")


conn.close()

print("\nDatabase connection closed.")
