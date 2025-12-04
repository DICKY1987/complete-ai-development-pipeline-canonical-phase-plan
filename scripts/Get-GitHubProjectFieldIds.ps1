<#
.SYNOPSIS
    Helper script to discover GitHub Project field and option IDs.

.DESCRIPTION
    Uses GitHub GraphQL API to fetch project structure including:
    - Project node ID (PROJECT_ID)
    - Status field ID (STATUS_FIELD_ID)
    - Status option IDs (for each status value)

    Outputs environment variable assignments ready to copy-paste.

.EXAMPLE
    # Find IDs for project #1 owned by current user
    pwsh scripts/Get-GitHubProjectFieldIds.ps1 -ProjectNumber 1 -Owner '@me'

.EXAMPLE
    # For an organization project
    pwsh scripts/Get-GitHubProjectFieldIds.ps1 -ProjectNumber 5 -Owner 'myorg'
#>

[CmdletBinding()]
param(
    # GitHub Project number
    [Parameter(Mandatory = $true)]
    [int]$ProjectNumber,

    # Project owner (@me or org name)
    [Parameter(Mandatory = $false)]
    [string]$Owner = '@me'
)

Write-Host "Fetching project structure for Project #$ProjectNumber (owner: $Owner)...`n"

# Get project node ID
Write-Verbose "Querying project list..."
$projectsJson = gh project list --owner $Owner --format json 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Failed to list projects: $projectsJson"
}

$projects = $projectsJson | ConvertFrom-Json
$project = $projects | Where-Object { $_.number -eq $ProjectNumber }

if (-not $project) {
    throw "Project #$ProjectNumber not found for owner '$Owner'"
}

$projectId = $project.id
Write-Host "✓ Project ID: $projectId"
Write-Host "  Title: $($project.title)"
Write-Host ""

# Query project fields using GraphQL
$query = @"
{
  node(id: \"$projectId\") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
            dataType
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            dataType
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}
"@

Write-Verbose "Querying project fields..."
$fieldsJson = gh api graphql -f query=$query 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Failed to query project fields: $fieldsJson"
}

$response = $fieldsJson | ConvertFrom-Json
$fields = $response.data.node.fields.nodes

# Find Status field
$statusField = $fields | Where-Object {
    $_.name -match '^Status$' -and $_.dataType -eq 'SINGLE_SELECT'
}

if (-not $statusField) {
    Write-Warning "No 'Status' field found. Available fields:"
    $fields | ForEach-Object {
        Write-Host "  - $($_.name) ($($_.dataType))"
    }
    Write-Host "`nYou may need to create a 'Status' field in your project."
    exit 1
}

Write-Host "✓ Status Field ID: $($statusField.id)"
Write-Host "  Options:"

$optionMap = @{}
foreach ($option in $statusField.options) {
    Write-Host "    - $($option.name): $($option.id)"

    # Try to map common names
    $normalizedName = $option.name.ToLower() -replace '\s+', '_'
    switch -Regex ($normalizedName) {
        '^(todo|not_started|backlog)' { $optionMap['todo'] = $option.id }
        '^(in_progress|in_work|doing)' { $optionMap['in_progress'] = $option.id }
        '^(done|complete|completed)' { $optionMap['done'] = $option.id }
        '^(blocked|on_hold)' { $optionMap['blocked'] = $option.id }
    }
}

Write-Host "`n" + ("=" * 70)
Write-Host "COPY AND PASTE THESE ENVIRONMENT VARIABLES:"
Write-Host ("=" * 70)
Write-Host ""
Write-Host "# PowerShell"
Write-Host "`$env:PROJECT_ID = '$projectId'"
Write-Host "`$env:STATUS_FIELD_ID = '$($statusField.id)'"

if ($optionMap['todo']) {
    Write-Host "`$env:STATUS_TODO_ID = '$($optionMap['todo'])'"
} else {
    Write-Host "# `$env:STATUS_TODO_ID = '<YOUR_TODO_OPTION_ID>'  # Not auto-detected"
}

if ($optionMap['in_progress']) {
    Write-Host "`$env:STATUS_IN_PROGRESS_ID = '$($optionMap['in_progress'])'"
} else {
    Write-Host "# `$env:STATUS_IN_PROGRESS_ID = '<YOUR_IN_PROGRESS_ID>'  # Not auto-detected"
}

if ($optionMap['done']) {
    Write-Host "`$env:STATUS_DONE_ID = '$($optionMap['done'])'"
} else {
    Write-Host "# `$env:STATUS_DONE_ID = '<YOUR_DONE_OPTION_ID>'  # Not auto-detected"
}

if ($optionMap['blocked']) {
    Write-Host "`$env:STATUS_BLOCKED_ID = '$($optionMap['blocked'])'"
} else {
    Write-Host "# `$env:STATUS_BLOCKED_ID = '<YOUR_BLOCKED_ID>'  # Optional"
}

Write-Host ""
Write-Host "# Bash/Zsh"
Write-Host "export PROJECT_ID='$projectId'"
Write-Host "export STATUS_FIELD_ID='$($statusField.id)'"

if ($optionMap['todo']) {
    Write-Host "export STATUS_TODO_ID='$($optionMap['todo'])'"
}
if ($optionMap['in_progress']) {
    Write-Host "export STATUS_IN_PROGRESS_ID='$($optionMap['in_progress'])'"
}
if ($optionMap['done']) {
    Write-Host "export STATUS_DONE_ID='$($optionMap['done'])'"
}
if ($optionMap['blocked']) {
    Write-Host "export STATUS_BLOCKED_ID='$($optionMap['blocked'])'"
}

Write-Host ""
Write-Host ("=" * 70)
Write-Host ""
Write-Host "After setting these, you can run:"
Write-Host "  pwsh scripts/Sync-UetPhaseStatusToGitHub.ps1 -PlanPath 'plans/WEEK2.yaml'"
Write-Host ""
