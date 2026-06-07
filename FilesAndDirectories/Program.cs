using System.Text;
using System.Text.Json;

GenerateSalesSummaryReport("stores", "salesSummary.txt");

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
        fileTotals.Add((file, fileTotal));
    }

    reportBuilder.AppendLine($"Total Sales: {grandTotal:C}");
    reportBuilder.AppendLine("Details:");

    foreach (var item in fileTotals)
    {
        reportBuilder.AppendLine($" {item.FileName}: {item.TotalSales:C}");
    }

    File.WriteAllText(reportFilePath, reportBuilder.ToString());

    Console.WriteLine("Sales summary report generated successfully.");
}

public class SalesTotal
{
    public decimal Total { get; set; }
}
