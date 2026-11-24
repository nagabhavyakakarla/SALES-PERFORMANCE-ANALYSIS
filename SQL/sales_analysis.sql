
/* =====================================================
   PROJECT: SALES PERFORMANCE ANALYSIS
   DATABASE: SalesAnalysisDB
   TABLE: dbo.SampleSuperstore
   ===================================================== */

USE SalesAnalysisDB;
GO

/* 1. DATA VALIDATION */

-- Total records
SELECT COUNT(*) AS Total_Records
FROM dbo.SampleSuperstore;

-- Duplicate Row IDs
SELECT ROW_ID, COUNT(*) AS Duplicate_Count
FROM dbo.SampleSuperstore
GROUP BY ROW_ID
HAVING COUNT(*) > 1;

-- Missing values
SELECT
    SUM(CASE WHEN Order_ID IS NULL THEN 1 ELSE 0 END) AS Missing_Order_ID,
    SUM(CASE WHEN Order_Date IS NULL THEN 1 ELSE 0 END) AS Missing_Order_Date,
    SUM(CASE WHEN Customer_ID IS NULL THEN 1 ELSE 0 END) AS Missing_Customer_ID,
    SUM(CASE WHEN Product_ID IS NULL THEN 1 ELSE 0 END) AS Missing_Product_ID,
    SUM(CASE WHEN Sales IS NULL THEN 1 ELSE 0 END) AS Missing_Sales,
    SUM(CASE WHEN Profit IS NULL THEN 1 ELSE 0 END) AS Missing_Profit
FROM dbo.SampleSuperstore;

-- Negative sales and profit
SELECT *
FROM dbo.SampleSuperstore
WHERE Sales < 0 OR Profit < 0;


/* 2. OVERALL BUSINESS KPIs */

SELECT
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    COUNT(DISTINCT Customer_ID) AS Total_Customers,
    SUM(Quantity) AS Total_Quantity,
    AVG(Sales) AS Average_Sales,
    AVG(Profit) AS Average_Profit,
    SUM(Profit) * 100.0 /
        NULLIF(SUM(Sales), 0) AS Profit_Margin_Percentage
FROM dbo.SampleSuperstore;


/* 3. CATEGORY-WISE PERFORMANCE */

SELECT
    Category,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    SUM(Quantity) AS Total_Quantity,
    COUNT(DISTINCT Order_ID) AS Total_Orders
FROM dbo.SampleSuperstore
GROUP BY Category
ORDER BY Total_Profit DESC;


/* 4. SUB-CATEGORY PERFORMANCE */

SELECT
    Category,
    Sub_Category,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    SUM(Quantity) AS Total_Quantity
FROM dbo.SampleSuperstore
GROUP BY Category, Sub_Category
ORDER BY Total_Profit DESC;


/* 5. REGIONAL PERFORMANCE */

SELECT
    Region,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    SUM(Profit) * 100.0 /
        NULLIF(SUM(Sales), 0) AS Profit_Margin
FROM dbo.SampleSuperstore
GROUP BY Region
ORDER BY Total_Sales DESC;


/* 6. TOP 10 STATES BY SALES */

SELECT TOP 10
    State,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM dbo.SampleSuperstore
GROUP BY State
ORDER BY Total_Sales DESC;


/* 7. TOP 10 CUSTOMERS */

SELECT TOP 10
    Customer_ID,
    Customer_Name,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    COUNT(DISTINCT Order_ID) AS Total_Orders
FROM dbo.SampleSuperstore
GROUP BY Customer_ID, Customer_Name
ORDER BY Total_Sales DESC;


/* 8. MONTHLY SALES TRENDS */

SELECT
    YEAR(Order_Date) AS Order_Year,
    MONTH(Order_Date) AS Order_Month,
    SUM(Sales) AS Monthly_Sales,
    SUM(Profit) AS Monthly_Profit,
    COUNT(DISTINCT Order_ID) AS Total_Orders
FROM dbo.SampleSuperstore
GROUP BY YEAR(Order_Date), MONTH(Order_Date)
ORDER BY Order_Year, Order_Month;


/* 9. YEAR-WISE PERFORMANCE */

SELECT
    YEAR(Order_Date) AS Order_Year,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    COUNT(DISTINCT Order_ID) AS Total_Orders
FROM dbo.SampleSuperstore
GROUP BY YEAR(Order_Date)
ORDER BY Order_Year;


/* 10. DISCOUNT IMPACT */

SELECT
    CASE
        WHEN Discount = 0 THEN 'No Discount'
        WHEN Discount <= 0.10 THEN '0-10%'
        WHEN Discount <= 0.20 THEN '11-20%'
        WHEN Discount <= 0.30 THEN '21-30%'
        ELSE 'Above 30%'
    END AS Discount_Range,
    COUNT(*) AS Total_Records,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    AVG(Profit) AS Average_Profit
FROM dbo.SampleSuperstore
GROUP BY
    CASE
        WHEN Discount = 0 THEN 'No Discount'
        WHEN Discount <= 0.10 THEN '0-10%'
        WHEN Discount <= 0.20 THEN '11-20%'
        WHEN Discount <= 0.30 THEN '21-30%'
        ELSE 'Above 30%'
    END
ORDER BY Discount_Range;


/* 11. SHIPPING PERFORMANCE */

SELECT
    Ship_Mode,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    AVG(CAST(DATEDIFF(DAY, Order_Date, Ship_Date)
        AS FLOAT)) AS Average_Shipping_Days,
    SUM(Sales) AS Total_Sales
FROM dbo.SampleSuperstore
GROUP BY Ship_Mode
ORDER BY Average_Shipping_Days;


/* 12. TOP 10 PROFITABLE PRODUCTS */

SELECT TOP 10
    Product_ID,
    Product_Name,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM dbo.SampleSuperstore
GROUP BY Product_ID, Product_Name
ORDER BY Total_Profit DESC;


/* 13. LOSS-MAKING PRODUCTS */

SELECT
    Product_ID,
    Product_Name,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM dbo.SampleSuperstore
GROUP BY Product_ID, Product_Name
HAVING SUM(Profit) < 0
ORDER BY Total_Profit;


/* 14. RUNNING TOTAL OF MONTHLY SALES */

WITH MonthlySales AS
(
    SELECT
        DATEFROMPARTS(
            YEAR(Order_Date),
            MONTH(Order_Date),
            1
        ) AS Sales_Month,
        SUM(Sales) AS Monthly_Sales
    FROM dbo.SampleSuperstore
    GROUP BY YEAR(Order_Date), MONTH(Order_Date)
)
SELECT
    Sales_Month,
    Monthly_Sales,
    SUM(Monthly_Sales) OVER (
        ORDER BY Sales_Month
        ROWS BETWEEN UNBOUNDED PRECEDING
        AND CURRENT ROW
    ) AS Running_Total_Sales
FROM MonthlySales
ORDER BY Sales_Month;


/* 15. RANK PRODUCTS WITHIN EACH CATEGORY */

WITH ProductSales AS
(
    SELECT
        Category,
        Product_Name,
        SUM(Sales) AS Total_Sales
    FROM dbo.SampleSuperstore
    GROUP BY Category, Product_Name
)
SELECT
    Category,
    Product_Name,
    Total_Sales,
    DENSE_RANK() OVER (
        PARTITION BY Category
        ORDER BY Total_Sales DESC
    ) AS Product_Rank
FROM ProductSales
ORDER BY Category, Product_Rank;


/* 16. CUSTOMER SEGMENT ANALYSIS */

SELECT
    Segment,
    COUNT(DISTINCT Customer_ID) AS Total_Customers,
    COUNT(DISTINCT Order_ID) AS Total_Orders,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM dbo.SampleSuperstore
GROUP BY Segment
ORDER BY Total_Sales DESC;


/* 17. ORDER SHIPPING DELAY ANALYSIS */

SELECT
    Ship_Mode,
    MIN(DATEDIFF(DAY, Order_Date, Ship_Date)) AS Minimum_Days,
    MAX(DATEDIFF(DAY, Order_Date, Ship_Date)) AS Maximum_Days,
    AVG(CAST(DATEDIFF(DAY, Order_Date, Ship_Date)
        AS FLOAT)) AS Average_Days
FROM dbo.SampleSuperstore
GROUP BY Ship_Mode;


/* 18. SALES CONTRIBUTION BY CATEGORY */

SELECT
    Category,
    SUM(Sales) AS Category_Sales,
    SUM(Sales) * 100.0 /
        NULLIF((SELECT SUM(Sales)
                FROM dbo.SampleSuperstore), 0)
        AS Sales_Contribution_Percentage
FROM dbo.SampleSuperstore
GROUP BY Category
ORDER BY Category_Sales DESC;


/* 19. HIGH-VALUE ORDERS */

SELECT
    Order_ID,
    Customer_Name,
    SUM(Sales) AS Order_Value
FROM dbo.SampleSuperstore
GROUP BY Order_ID, Customer_Name
HAVING SUM(Sales) > 1000
ORDER BY Order_Value DESC;


/* 20. FINAL BUSINESS SUMMARY */

SELECT
    COUNT(*) AS Total_Records,
    COUNT(DISTINCT Order_ID) AS Unique_Orders,
    COUNT(DISTINCT Customer_ID) AS Unique_Customers,
    SUM(Sales) AS Total_Revenue,
    SUM(Profit) AS Total_Profit,
    SUM(Quantity) AS Total_Units_Sold,
    SUM(Profit) * 100.0 /
        NULLIF(SUM(Sales), 0) AS Profit_Margin
FROM dbo.SampleSuperstore;
GO
