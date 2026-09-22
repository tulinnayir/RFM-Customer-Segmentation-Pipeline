USE AdventureWorks2025;
GO

-- Customer-based total orders, spending, and line item value analysis
SELECT 
    c.CustomerID,
    p.FirstName + ' ' + p.LastName AS CustomerName,
    COUNT(DISTINCT soh.SalesOrderID) AS TotalOrders,
    SUM(sod.LineTotal) AS TotalSpent,
    AVG(sod.LineTotal) AS AvgOrderLineValue,
    MAX(soh.OrderDate) AS LastOrderDate
FROM Sales.Customer c
INNER JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
INNER JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
INNER JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
GROUP BY 
    c.CustomerID, 
    p.FirstName, 
    p.LastName;

WITH CustomerRFM AS (
    -- Stage 1: Calculate raw RFM metrics for each customer
    SELECT 
        c.CustomerID,
        p.FirstName + ' ' + p.LastName AS CustomerName,
        DATEDIFF(day, MAX(soh.OrderDate), (SELECT MAX(OrderDate) FROM Sales.SalesOrderHeader)) AS Recency, -- Days since the last order
        COUNT(DISTINCT soh.SalesOrderID) AS Frequency, -- Total number of orders
        SUM(sod.LineTotal) AS Monetary -- Total monetary spend
    FROM Sales.Customer c
    INNER JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
    INNER JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
    INNER JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
    GROUP BY c.CustomerID, p.FirstName, p.LastName
),
RFMScores AS (
    -- Stage 2: Assign 1-5 scores using NTILE window functions
    SELECT 
        CustomerID,
        CustomerName,
        Recency,
        Frequency,
        Monetary,
        NTILE(5) OVER (ORDER BY Recency ASC) AS R_Score, -- Lower days = Better score
        NTILE(5) OVER (ORDER BY Frequency DESC) AS F_Score,
        NTILE(5) OVER (ORDER BY Monetary DESC) AS M_Score
    FROM CustomerRFM
)
-- Stage 3: Combine scores and determine the final customer segment
SELECT 
    CustomerID,
    CustomerName,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    (CAST(R_Score AS VARCHAR) + CAST(F_Score AS VARCHAR) + CAST(M_Score AS VARCHAR)) AS RFM_Cell,
    CASE 
        WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions'
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal Customers'
        WHEN R_Score <= 2 AND F_Score >= 4 THEN 'At Risk'
        WHEN R_Score >= 4 AND F_Score <= 2 THEN 'New Customers'
        ELSE 'Potential Loyalist'
    END AS CustomerSegment
FROM RFMScores
ORDER BY Monetary DESC;