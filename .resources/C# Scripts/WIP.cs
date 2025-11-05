// Loop through all tables in the model
foreach (var table in Model.Tables)
{
    if (table == null || table.IsHidden) continue;

    foreach (var column in table.Columns)
    {
        if (column == null) continue;

        // Case-insensitive check for SK or ID at the end
        var colNameUpper = column.Name.ToUpper();
        if (colNameUpper.EndsWith("SK") || colNameUpper.EndsWith("ID"))
        {
            // Move column to "Keys" folder
            column.DisplayFolder = "Keys";

            // Optional: hide the column in client tools
            column.IsHidden = true;
            
            // Set IsAvailableInMDX to False to prevent these columns being used by Analyze in Excel. IDs have no place in Analyze in Excel, this is for analyst.
            column.IsAvailableInMDX = false;
            column.IsKey = true;
        }
    }
}
