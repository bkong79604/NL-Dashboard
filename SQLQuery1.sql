-- Please show me the total Tax Amount by territory
SELECT TOP 5 b.Name, SUM(a.TaxAmt) AS TOTALTAXAMOUNT
  FROM [AdventureWorks2022].[Sales].[SalesOrderHeader] a
  INNER JOIN [Sales].[SalesTerritory] b ON a.TerritoryID = b.TerritoryID
  GROUP BY b.Name
  ORDER BY SUM(a.TaxAmt) DESC;
  
-- use a pie chart to show the top 3 territory with the most customer count
SELECT TOP 3 b.Name, COUNT(*) AS TOTAL_CUSTOMERS
  FROM [AdventureWorks2022].[Sales].[Customer] a
  INNER JOIN [Sales].[SalesTerritory] b ON a.TerritoryID = b.TerritoryID
  GROUP BY b.Name
  ORDER BY COUNT(*) DESC;

-- use a bar chart to show the top 5 territories with the most order count
SELECT TOP 5 b.Name, COUNT(*) AS ORDER_COUNT
  FROM [AdventureWorks2022].[Sales].[SalesOrderHeader] a
  INNER JOIN [Sales].[SalesTerritory] b ON a.TerritoryID = b.TerritoryID
  GROUP BY b.Name
  ORDER BY COUNT(*) DESC;

-- how many orders we have for ship date = '2011-06-07'?
SELECT COUNT(*) AS ORDER_COUNT
  FROM [AdventureWorks2022].[Sales].[SalesOrderHeader]
  WHERE ShipDate = '2011-06-07 00:00:00.000';