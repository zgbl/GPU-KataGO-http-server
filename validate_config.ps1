# KataGo Configuration Validator
# Check common issues in KataGo configuration files

param(
    [string]$ConfigPath = "configs\katago_gtp.cfg"
)

$ErrorActionPreference = "Stop"

Write-Host "KataGo Configuration Validator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if config file exists
if (-not (Test-Path $ConfigPath)) {
    Write-Host "ERROR: Configuration file not found: $ConfigPath" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Configuration file exists: $ConfigPath" -ForegroundColor Green

# Read configuration file content
$configContent = Get-Content $ConfigPath
$issues = @()
$warnings = @()

# Parse configuration file and extract keys
$keys = @{}
foreach ($line in $configContent) {
    $line = $line.Trim()
    # Skip comment lines and empty lines
    if ($line.StartsWith('#') -or $line -eq '') {
        continue
    }
    # Match configuration key = value pattern (handle mixed content lines)
    if ($line -match '([a-zA-Z][a-zA-Z0-9_]*)\s*=\s*[^#]*') {
        $key = $matches[1]
        if ($keys.ContainsKey($key)) {
            $issues += "Duplicate key: $key"
        } else {
            $keys[$key] = $true
        }
    }
}

Write-Host ""
Write-Host "Checking for duplicate keys..." -ForegroundColor Yellow
Write-Host "Checking for rule configuration conflicts..." -ForegroundColor Yellow
Write-Host "Checking other configuration issues..." -ForegroundColor Yellow

# Check for rule conflicts
$hasRules = $keys.ContainsKey('rules')
$individualRules = @('koRule', 'scoringRule', 'taxRule', 'multiStoneSuicideLegal', 'hasButton', 'whiteHandicapBonus')
$foundIndividualRules = @()

foreach ($rule in $individualRules) {
    if ($keys.ContainsKey($rule)) {
        $foundIndividualRules += $rule
    }
}

if ($hasRules -and $foundIndividualRules.Count -gt 0) {
    $issues += "Rule conflict: Both 'rules' and individual rule items found: $($foundIndividualRules -join ', ')"
}

# Check for other configuration issues

# Check for required configuration items using simple string search
$requiredKeys = @('nnCacheSizePowerOfTwo', 'nnMaxBatchSize', 'numSearchThreads')
foreach ($requiredKey in $requiredKeys) {
    $found = $false
    foreach ($line in $configContent) {
        if ($line -match "$requiredKey\s*=") {
            $found = $true
            break
        }
    }
    if (-not $found) {
        $warnings += "Missing recommended configuration: $requiredKey"
    }
}

# Check for potentially invalid configurations
$deprecatedKeys = @('numGpus', 'gpuToUse')
foreach ($deprecatedKey in $deprecatedKeys) {
    if ($keys.ContainsKey($deprecatedKey)) {
        $warnings += "Potentially deprecated configuration: $deprecatedKey"
    }
}

# Output results
Write-Host ""
Write-Host "Validation Results:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "OK: No critical issues found" -ForegroundColor Green
} else {
    Write-Host "ERROR: Found $($issues.Count) issue(s):" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "WARNING: Found $($warnings.Count) warning(s):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

# Provide fix suggestions
if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "Fix Suggestions:" -ForegroundColor Cyan
    
    foreach ($issue in $issues) {
        if ($issue -like "*Duplicate key*") {
            Write-Host "  - Remove duplicate configuration lines, ensure each key appears only once" -ForegroundColor White
        }
        if ($issue -like "*Rule conflict*") {
            Write-Host "  - Remove individual rule items, keep only 'rules = tromp-taylor'" -ForegroundColor White
            Write-Host "  - Or remove 'rules' line and use individual rule settings" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "Please fix the issues and run this script again." -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "SUCCESS: Configuration file validation passed!" -ForegroundColor Green
exit 0