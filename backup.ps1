# GPU-KataGO HTTP Server Backup Script
# Author: Auto-generated
# Purpose: Backup important files to releases folder

param(
    [string]$BackupName = "backup"
)

# Get current script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir

# Create timestamp
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupFolderName = "${BackupName}_${Timestamp}"
$BackupPath = Join-Path $ProjectRoot "releases\$BackupFolderName"

Write-Host "=== GPU-KataGO HTTP Server Backup Script ===" -ForegroundColor Green
Write-Host "Backup Time: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Backup Target: $BackupPath" -ForegroundColor Yellow

# Create backup directory
try {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    Write-Host "[OK] Created backup directory: $BackupPath" -ForegroundColor Green
} catch {
    Write-Error "[ERROR] Cannot create backup directory: $_"
    exit 1
}

# Define important files and folders to backup
$ImportantItems = @(
    # Main server files
    "katago_analysis_server.py",
    "http_test.py",
    "container_diagnostic.py",
    
    # Configuration files
    "configs",
    "docker-compose.integrated.yml",
    "Dockerfile.integrated",
    
    # Documentation
    "README.md",
    "README_INTEGRATED.md",
    "API_DOCUMENTATION.md",
    "QUICK_START.md",
    "TROUBLESHOOTING.md",
    "VERSION_DIFFERENCES.md",
    "SGF_TESTER_README.md",
    
    # Script files
    "build_and_run.ps1",
    "build_and_run.sh",
    "health_check.ps1",
    "health_check.sh",
    "debug_katago.sh",
    "validate_config.ps1",
    
    # Test files
    "Pythontest",
    
    # Documentation directory
    "Doc"
)

# Backup file counters
$BackupCount = 0
$SkipCount = 0

# Execute backup
foreach ($Item in $ImportantItems) {
    $SourcePath = Join-Path $ProjectRoot $Item
    $DestPath = Join-Path $BackupPath $Item
    
    if (Test-Path $SourcePath) {
        try {
            if (Test-Path $SourcePath -PathType Container) {
                # Backup folder
                Copy-Item -Path $SourcePath -Destination $DestPath -Recurse -Force
                Write-Host "[OK] Backed up folder: $Item" -ForegroundColor Green
            } else {
                # Backup file
                $DestDir = Split-Path $DestPath -Parent
                if (!(Test-Path $DestDir)) {
                    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
                }
                Copy-Item -Path $SourcePath -Destination $DestPath -Force
                Write-Host "[OK] Backed up file: $Item" -ForegroundColor Green
            }
            $BackupCount++
        } catch {
            Write-Warning "[WARNING] Backup failed: $Item - $_"
            $SkipCount++
        }
    } else {
        Write-Warning "[WARNING] File not found, skipping: $Item"
        $SkipCount++
    }
}

# Create backup information file
$BackupInfo = @"
# Backup Information
Backup Time: $(Get-Date)
Backup Name: $BackupName
Project Path: $ProjectRoot
Backup Path: $BackupPath
Successful Backups: $BackupCount items
Skipped Items: $SkipCount items

# Backup Content List
"@

foreach ($Item in $ImportantItems) {
    $SourcePath = Join-Path $ProjectRoot $Item
    if (Test-Path $SourcePath) {
        $BackupInfo += "`n[OK] $Item"
    } else {
        $BackupInfo += "`n[SKIP] $Item (not found)"
    }
}

$BackupInfoPath = Join-Path $BackupPath "BACKUP_INFO.txt"
$BackupInfo | Out-File -FilePath $BackupInfoPath -Encoding UTF8

# Display backup results
Write-Host "`n=== Backup Completed ===" -ForegroundColor Green
Write-Host "Backup Location: $BackupPath" -ForegroundColor Yellow
Write-Host "Successful Backups: $BackupCount items" -ForegroundColor Green
Write-Host "Skipped Items: $SkipCount items" -ForegroundColor Yellow
Write-Host "Backup Info: $BackupInfoPath" -ForegroundColor Cyan

# Display backup folder size
try {
    $BackupSize = (Get-ChildItem -Path $BackupPath -Recurse | Measure-Object -Property Length -Sum).Sum
    $BackupSizeMB = [math]::Round($BackupSize / 1MB, 2)
    Write-Host "Backup Size: $BackupSizeMB MB" -ForegroundColor Cyan
} catch {
    Write-Host "Cannot calculate backup size" -ForegroundColor Yellow
}

Write-Host "`nBackup script execution completed!" -ForegroundColor Green