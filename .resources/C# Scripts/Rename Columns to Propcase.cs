// -----------------------------------------------------------------------------
// Script: Convert snake_case to words with spaces
//          - Capitalize only the first word
//          - Keep spaces intact
//          - Capitalize "ID" and "SK" suffixes
// Example: "customer_sk" -> "Customer SK"
//          "order_id" -> "Order ID"
//          "total_order_value" -> "Total order value"
// -----------------------------------------------------------------------------

foreach (var table in Model.Tables)
{
    foreach (var column in table.Columns)
    {
        string oldName = column.Name;

        // Replace underscores with spaces and lowercase everything
        string spaced = oldName.Replace("_", " ").ToLower();

        // Capitalize only the first word
        string newName = System.Globalization.CultureInfo.CurrentCulture.TextInfo
            .ToTitleCase(spaced).Substring(0, 1).ToUpper() + spaced.Substring(1);

        // Fix suffixes: make sure " id" and " sk" become uppercase
        if (newName.EndsWith(" id"))
            newName = newName.Substring(0, newName.Length - 3) + " ID";
        else if (newName.EndsWith(" sk"))
            newName = newName.Substring(0, newName.Length - 3) + " SK";

        // Apply only if the name changed
        if (oldName != newName)
        {
            column.Name = newName;
            Output("Renamed: " + table.Name + "." + oldName + " -> " + newName);
        }
    }
}
