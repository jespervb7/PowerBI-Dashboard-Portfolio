// --- Model Cleanup & Standardization Script ---
// Description:
// 1. Skips tables in the ignore list.
// 2. Removes DIM/FACT and any prefix before it in table names.
// 3. Capitalizes only the first word of table and column names and removes underscores. ranking_number becomes Ranking number
// 4. Moves columns ending in ID or SK to a "Keys" folder and hides them.
// 5. Moves columns starting with "is" to a "Flags" folder.
// 6. Moves remaining columns to a "Columns" folder.

// List of tables to ignore and prevent errors (case-insensitive)
var ignoredTables = new[] { "_Measures", "Audit_Log", "Technical_Metadata" };

// ============================
// Main Loop
// ============================
foreach (var table in Model.Tables)
{
    // Skip ignored tables
    if (ignoredTables.Any(t => t.Equals(table.Name, System.StringComparison.OrdinalIgnoreCase)))
        continue;

    // ===========================
    // Handle TABLE NAME cleanup
    // ===========================
    string originalTableName = table.Name.Trim();
    string newTableName = originalTableName;

    // Remove everything up to and including DIM_ / DIM / FACT_ / FACT (case-insensitive)
    newTableName = System.Text.RegularExpressions.Regex.Replace(newTableName, @"(?i)^.*?(DIM[_\s]|FACT[_\s])", "");

    // Replace underscores with spaces and collapse multiple spaces
    newTableName = System.Text.RegularExpressions.Regex.Replace(newTableName.Replace("_", " "), "\\s+", " ").Trim();

    // Lowercase then capitalize only the first letter
    if (newTableName.Length > 0)
        newTableName = char.ToUpper(newTableName[0]) + newTableName.Substring(1).ToLower();

    // Rename table if changed
    if (table.Name != newTableName)
        table.Name = newTableName;


    // ===========================
    // Handle COLUMN cleanup
    // ===========================
    foreach (var column in table.Columns)
        
    {
        var colName = column.Name;
        var colNameLower = colName.ToLower();
        
        if (colNameLower.StartsWith("is"))
        {
            column.DisplayFolder = "Flags";
        }
       
        else {column.DisplayFolder = "Columns";}
        
        string originalName = column.Name.Trim();

        // Normalize: replace underscores with spaces, collapse multiple spaces, trim
        string newName = System.Text.RegularExpressions.Regex.Replace(originalName.Replace("_", " "), "\\s+", " ").Trim();

        // Lowercase everything first (we will only uppercase the very first letter)
        newName = newName.ToLower();

        // Capitalize only the first character (if any)
        if (newName.Length > 0)
            newName = char.ToUpper(newName[0]) + newName.Substring(1);

        // Determine if column is a key (ends with id or sk, with optional separator)
        bool isKeyColumn = System.Text.RegularExpressions.Regex.IsMatch(originalName, "(?i)(?:_|\\s)?(?:id|sk)$");

        if (isKeyColumn)
        {
            // Ensure the trailing ID / SK is uppercase (only when at end of string)
            newName = System.Text.RegularExpressions.Regex.Replace(newName, "(?i)\\b(id)$", "ID");
            newName = System.Text.RegularExpressions.Regex.Replace(newName, "(?i)\\b(sk)$", "SK");

            // Build description base by removing trailing ID / SK (and any trailing space)
            string nameForDescription = System.Text.RegularExpressions.Regex.Replace(newName, "(?i)[ _]*ID$", "");
            nameForDescription = System.Text.RegularExpressions.Regex.Replace(nameForDescription, "(?i)[ _]*SK$", "");
            nameForDescription = nameForDescription.Trim();

            // Apply attributes for keys
            column.DisplayFolder = "Keys";
            column.IsAvailableInMDX = false;
            column.IsHidden = true;
            column.Description = "This is the key of the " + nameForDescription + " dimension and is used in relationships for Power ";
        }

        // Apply rename if needed
        if (column.Name != newName)
            column.Name = newName;
    }
}
