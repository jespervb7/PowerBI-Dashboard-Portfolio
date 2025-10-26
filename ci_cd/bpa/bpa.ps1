param (
    # Default to searching in all semantic model folders
    $src = @("**\*.SemanticModel")        
)
  
$currentFolder = (Split-Path $MyInvocation.MyCommand.Definition -Parent)

if ($src.Length -eq 0) {
    Write-Host "Please provide a valid path to the source files."
    return
}

#region: Tools download

$toolsPath = "$currentFolder\_tools"

$tools = @(
    @{
        "tool" = "TabularEditor"
        "downloadUrl" = "https://github.com/TabularEditor/TabularEditor/releases/latest/download/TabularEditor.Portable.zip"
        "rulesUrl" = "https://raw.githubusercontent.com/microsoft/Analysis-Services/master/BestPracticeRules/BPARules.json" 
    }
)

foreach ($tool in $tools) {
    $toolName = $tool.tool
    $downloadUrl = $tool.downloadUrl
    $rulesUrl = $tool.rulesUrl
    $destinationPath = "$toolsPath\$toolName"

    if (!(Test-Path $destinationPath)) {
        Write-Host "Creating directory for $toolName..."
        New-Item -ItemType Directory -Path $destinationPath -ErrorAction SilentlyContinue | Out-Null            

        Write-Host "Downloading $toolName..."
        $zipFile = "$destinationPath\$toolName.zip"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile
        
        Write-Host "Extracting $toolName..."
        Expand-Archive -Path $zipFile -DestinationPath $destinationPath -Force     
        Remove-Item $zipFile        

        Write-Host "Downloading default rules..."
        Invoke-WebRequest -Uri $rulesUrl -OutFile "$destinationPath\defaultRules.json"
    }    
}

#endregion

#region Run Tabular Editor BPA

$tabularEditorExe = "$toolsPath\TabularEditor\TabularEditor.exe"
$tabularEditorRulesPath = "$currentFolder\bpa-rules-semanticmodel.json"

if (!(Test-Path $tabularEditorRulesPath)) {
    Write-Host "Using default rules for Tabular Editor"
    $tabularEditorRulesPath = "$toolsPath\TabularEditor\defaultRules.json"
}

$repoRoot = Split-Path (Split-Path $currentFolder -Parent) -Parent
$results = @()

# Search for semantic model folders
Get-ChildItem -Path $repoRoot -Recurse -Directory -Filter "*.SemanticModel" | ForEach-Object {
    $semanticModelPath = $_.FullName
    $modelName = Split-Path $semanticModelPath -Leaf
    Write-Host "Processing semantic model: $modelName"

    # Look for model.tmdl file
    $tmdlPath = Join-Path $semanticModelPath "definition\model.tmdl"
    
    if (Test-Path $tmdlPath) {
        Write-Host "Running Tabular Editor BPA rules for: '$tmdlPath'"
        
        try {
            $process = Start-Process -FilePath $tabularEditorExe -ArgumentList """$tmdlPath"" -A ""$tabularEditorRulesPath"" -G" -NoNewWindow -Wait -PassThru    

            $result = @{
                "ModelName" = $modelName
                "Path" = $tmdlPath
                "Success" = $process.ExitCode -eq 0
                "ErrorCode" = $process.ExitCode
            }

            $results += [PSCustomObject]$result

            if ($process.ExitCode -ne 0) {
                Write-Warning "Error running rules for: '$tmdlPath' (Exit code: $($process.ExitCode))"
            }
        }
        catch {
            Write-Error "Failed to process '$tmdlPath': $_"
            $result = @{
                "ModelName" = $modelName
                "Path" = $tmdlPath
                "Success" = $false
                "ErrorCode" = -1
                "Error" = $_.Exception.Message
            }
            $results += [PSCustomObject]$result
        }
    }
    else {
        Write-Warning "No model.tmdl file found in: $semanticModelPath"
    }
}

# Output summary
Write-Host "`nBest Practice Analysis Summary:"
Write-Host "=============================="
$results | Format-Table ModelName, Success, ErrorCode

# Return results object for pipeline usage
$results
#endregion