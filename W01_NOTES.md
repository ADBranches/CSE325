# CSE 325 W01 Assignment: .NET Applications

## Student Name

Edwin Kambale

## Assignment Summary

This repository contains my completed work for the W01 Assignment: .NET Applications. The assignment includes work from the Microsoft learning modules for building .NET applications with C#, including creating a Web API with ASP.NET Core controllers and working with files and directories in a .NET app.

---

# Part 1: Create a Web API with ASP.NET Core Controllers

## Additional Pizza Record Added

I added the following additional pizza record to the Pizzas list:

```csharp
new Pizza { Id = 6, Name = "Chicken Supreme", IsGlutenFree = false }
```

---

## API Testing Evidence

### 1. GET All Pizzas

Request:

```http
GET http://localhost:5012/pizza
```

Returned status code:

```text
200 OK
```

Response example:

```json
[
  {
    "id": 1,
    "name": "Classic Italian",
    "isGlutenFree": false
  },
  {
    "id": 2,
    "name": "Veggie",
    "isGlutenFree": true
  },
  {
    "id": 3,
    "name": "Hawaiian",
    "isGlutenFree": false
  },
  {
    "id": 4,
    "name": "Meat Lovers",
    "isGlutenFree": false
  },
  {
    "id": 5,
    "name": "Margherita",
    "isGlutenFree": true
  },
  {
    "id": 6,
    "name": "Chicken Supreme",
    "isGlutenFree": false
  }
]
```

---

### 2. GET One Pizza

Request:

```http
GET http://localhost:5012/pizza/6
```

Returned status code:

```text
200 OK
```

Response example:

```json
{
  "id": 6,
  "name": "Chicken Supreme",
  "isGlutenFree": false
}
```

---

### 3. POST Create Pizza

Request:

```http
POST http://localhost:5012/pizza
Content-Type: application/json

{
  "name": "BBQ Chicken",
  "isGlutenFree": false
}
```

Returned status code:

```text
201 Created
```

Response example:

```json
{
  "id": 7,
  "name": "BBQ Chicken",
  "isGlutenFree": false
}
```

---

### 4. PUT Update Pizza

Request:

```http
PUT http://localhost:5012/pizza/7
Content-Type: application/json

{
  "id": 7,
  "name": "BBQ Chicken Deluxe",
  "isGlutenFree": false
}
```

Returned status code:

```text
204 No Content
```

Response body:

```text
No response body
```

---

### 5. DELETE Pizza

Request:

```http
DELETE http://localhost:5012/pizza/7
```

Returned status code:

```text
204 No Content
```

Response body:

```text
No response body
```

---

# Part 2: Work with Files and Directories in a .NET App

## Sales Summary Function

The following function generates a sales summary report file. The report includes the actual total sales from all sales files and a detailed report showing each file's total sales.

```csharp
using System.Text;
using System.Text.Json;

static void GenerateSalesSummaryReport(string rootFolder, string reportFilePath)
{
    decimal grandTotal = 0;
    var reportBuilder = new StringBuilder();

    reportBuilder.AppendLine("Sales Summary");
    reportBuilder.AppendLine("---------------------------");

    var fileTotals = new List<(string FileName, decimal TotalSales)>();

    foreach (var file in Directory.EnumerateFiles(rootFolder, "sales.json", SearchOption.AllDirectories))
    {
        decimal fileTotal = 0;

        using (var reader = File.OpenText(file))
        {
            var json = reader.ReadToEnd();

            var salesData = JsonSerializer.Deserialize<SalesTotal[]>(json);

            if (salesData != null)
            {
                foreach (var sale in salesData)
                {
                    fileTotal += sale.Total;
                }
            }
        }

        grandTotal += fileTotal;
        fileTotals.Add((Path.GetFileName(file), fileTotal));
    }

    reportBuilder.AppendLine($"Total Sales: {grandTotal:C}");
    reportBuilder.AppendLine("Details:");

    foreach (var item in fileTotals)
    {
        reportBuilder.AppendLine($" {item.FileName}: {item.TotalSales:C}");
    }

    File.WriteAllText(reportFilePath, reportBuilder.ToString());
}
```

Example function call:

```csharp
GenerateSalesSummaryReport("stores", "salesSummary.txt");
```

Example generated report:

```text
Sales Summary
---------------------------
Total Sales: $1,234,567.89
Details:
 sales.json: $123,456.78
 sales.json: $987,654.32
 sales.json: $123,456.79
```

---

# Completion Checklist

- Completed the required .NET learning modules.
- Added at least one additional record to the Pizzas list.
- Tested GET, POST, PUT, and DELETE API operations.
- Included returned status codes for each API operation.
- Added a sales summary report function.
- Included a text copy of the sales summary function in this notes file.
- Committed and pushed the completed work to the course repository.
