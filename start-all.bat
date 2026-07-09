@echo off
setlocal

set "ROOT=%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$bat = '%~f0'; $root = '%ROOT%'; $content = Get-Content -Raw -LiteralPath $bat; $script = ($content -split '### POWERSHELL_START ###')[-1]; $tmp = Join-Path $env:TEMP ('gradescope-start-' + [guid]::NewGuid().ToString() + '.ps1'); Set-Content -LiteralPath $tmp -Value $script -Encoding UTF8; try { & $tmp -Root $root } finally { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo GradeScope failed to start. See the error above.
    pause
)
exit /b %EXIT_CODE%

### POWERSHELL_START ###
param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$backendPath = Join-Path $rootPath "backend"
$frontendPath = Join-Path $rootPath "frontend"
$venvPython = Join-Path $rootPath ".venv\Scripts\python.exe"
$requirementsPath = Join-Path $backendPath "requirements.txt"
$nodeModulesPath = Join-Path $frontendPath "node_modules"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class JobApi
{
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool SetInformationJobObject(IntPtr hJob, int jobObjectInfoClass, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool CloseHandle(IntPtr hObject);
}

[StructLayout(LayoutKind.Sequential)]
public struct JOBOBJECT_BASIC_LIMIT_INFORMATION
{
    public long PerProcessUserTimeLimit;
    public long PerJobUserTimeLimit;
    public uint LimitFlags;
    public UIntPtr MinimumWorkingSetSize;
    public UIntPtr MaximumWorkingSetSize;
    public uint ActiveProcessLimit;
    public long Affinity;
    public uint PriorityClass;
    public uint SchedulingClass;
}

[StructLayout(LayoutKind.Sequential)]
public struct IO_COUNTERS
{
    public ulong ReadOperationCount;
    public ulong WriteOperationCount;
    public ulong OtherOperationCount;
    public ulong ReadTransferCount;
    public ulong WriteTransferCount;
    public ulong OtherTransferCount;
}

[StructLayout(LayoutKind.Sequential)]
public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
{
    public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
    public IO_COUNTERS IoInfo;
    public UIntPtr ProcessMemoryLimit;
    public UIntPtr JobMemoryLimit;
    public UIntPtr PeakProcessMemoryUsed;
    public UIntPtr PeakJobMemoryUsed;
}
"@

function New-KillOnCloseJob {
    $job = [JobApi]::CreateJobObject([IntPtr]::Zero, $null)
    if ($job -eq [IntPtr]::Zero) {
        throw "Could not create Windows Job object."
    }

    $info = New-Object JOBOBJECT_EXTENDED_LIMIT_INFORMATION
    $info.BasicLimitInformation.LimitFlags = 0x00002000
    $length = [Runtime.InteropServices.Marshal]::SizeOf($info)
    $pointer = [Runtime.InteropServices.Marshal]::AllocHGlobal($length)

    try {
        [Runtime.InteropServices.Marshal]::StructureToPtr($info, $pointer, $false)
        if (-not [JobApi]::SetInformationJobObject($job, 9, $pointer, [uint32]$length)) {
            throw "Could not configure Windows Job object."
        }
    }
    finally {
        [Runtime.InteropServices.Marshal]::FreeHGlobal($pointer)
    }

    return $job
}

function Start-ManagedWindow {
    param(
        [Parameter(Mandatory = $true)]
        [IntPtr]$Job,
        [Parameter(Mandatory = $true)]
        [string]$Title,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$ArgumentList = @()
    )

    $escapedFilePath = $FilePath.Replace("'", "''")
    $escapedArguments = @($ArgumentList | ForEach-Object { "'" + $_.Replace("'", "''") + "'" })
    $argumentLiteral = "@(" + ($escapedArguments -join ", ") + ")"
    $supervisorProcessId = $PID

    $windowScript = @"
`$Host.UI.RawUI.WindowTitle = "$Title"
`$ErrorActionPreference = "Stop"
Set-Location -LiteralPath "$WorkingDirectory"
Write-Host "$Title"
Write-Host "Working directory: $WorkingDirectory"
Write-Host ""

function Stop-ProcessTree {
    param([int]`$RootProcessId)

    `$rows = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
    `$ids = New-Object "System.Collections.Generic.HashSet[int]"
    [void]`$ids.Add(`$RootProcessId)

    `$changed = `$true
    while (`$changed) {
        `$changed = `$false
        foreach (`$row in `$rows) {
            if (`$ids.Contains([int]`$row.ParentProcessId) -and -not `$ids.Contains([int]`$row.ProcessId)) {
                [void]`$ids.Add([int]`$row.ProcessId)
                `$changed = `$true
            }
        }
    }

    foreach (`$processId in `$ids) {
        if (`$processId -ne `$PID) {
            Stop-Process -Id `$processId -Force -ErrorAction SilentlyContinue
        }
    }
}

`$commandProcess = `$null
try {
    `$commandProcess = Start-Process -FilePath '$escapedFilePath' -ArgumentList $argumentLiteral -NoNewWindow -PassThru
    while (`$true) {
        if (`$commandProcess.HasExited) {
            break
        }

        if (-not (Get-Process -Id $supervisorProcessId -ErrorAction SilentlyContinue)) {
            break
        }

        Start-Sleep -Milliseconds 500
    }
}
finally {
    if (`$commandProcess -and -not `$commandProcess.HasExited) {
        Stop-ProcessTree -RootProcessId `$commandProcess.Id
    }

    Write-Host ""
    Write-Host "$Title stopped. The launcher will close the other service too."
    Start-Sleep -Seconds 3
}
"@

    $bytes = [Text.Encoding]::Unicode.GetBytes($windowScript)
    $encodedCommand = [Convert]::ToBase64String($bytes)
    $process = Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-EncodedCommand",
        $encodedCommand
    ) -PassThru

    if (-not [JobApi]::AssignProcessToJobObject($Job, $process.Handle)) {
        throw "Could not attach $Title to the cleanup job."
    }

    return $process
}

function Add-ProcessTreeToJob {
    param(
        [Parameter(Mandatory = $true)]
        [IntPtr]$Job,
        [Parameter(Mandatory = $true)]
        [int[]]$RootProcessIds,
        [Parameter(Mandatory = $true)]
        [hashtable]$AssignedProcessIds
    )

    $processRows = @(Get-CimInstance Win32_Process)
    $knownIds = New-Object "System.Collections.Generic.HashSet[int]"

    foreach ($rootProcessId in $RootProcessIds) {
        if ($rootProcessId -gt 0) {
            [void]$knownIds.Add($rootProcessId)
        }
    }

    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($row in $processRows) {
            if ($knownIds.Contains([int]$row.ParentProcessId) -and -not $knownIds.Contains([int]$row.ProcessId)) {
                [void]$knownIds.Add([int]$row.ProcessId)
                $changed = $true
            }
        }
    }

    foreach ($processId in $knownIds) {
        if ($AssignedProcessIds.ContainsKey($processId)) {
            continue
        }

        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            [void][JobApi]::AssignProcessToJobObject($Job, $process.Handle)
            $AssignedProcessIds[$processId] = $true
        }
        catch {
            $AssignedProcessIds[$processId] = $true
        }
    }
}

function Stop-TrackedProcesses {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$AssignedProcessIds,
        [Parameter(Mandatory = $true)]
        [int[]]$RootProcessIds
    )

    $idsToStop = New-Object "System.Collections.Generic.HashSet[int]"

    foreach ($processId in $AssignedProcessIds.Keys) {
        if ([int]$processId -gt 0) {
            [void]$idsToStop.Add([int]$processId)
        }
    }

    $processRows = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
    foreach ($rootProcessId in $RootProcessIds) {
        if ($rootProcessId -gt 0) {
            [void]$idsToStop.Add($rootProcessId)
        }
    }

    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($row in $processRows) {
            if ($idsToStop.Contains([int]$row.ParentProcessId) -and -not $idsToStop.Contains([int]$row.ProcessId)) {
                [void]$idsToStop.Add([int]$row.ProcessId)
                $changed = $true
            }
        }
    }

    foreach ($processId in $idsToStop) {
        if ($processId -ne $PID) {
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-LoggedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$ArgumentList = @(),
        [string]$WorkingDirectory = $rootPath
    )

    Write-Host $Label
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -NoNewWindow -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "$Label failed with exit code $($process.ExitCode)."
    }
}

function New-GradeScopeVenv {
    $pyLauncher = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        Invoke-LoggedCommand -Label "Creating Python virtual environment..." -FilePath $pyLauncher.Source -ArgumentList @("-3", "-m", "venv", (Join-Path $rootPath ".venv"))
        return
    }

    $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($python) {
        Invoke-LoggedCommand -Label "Creating Python virtual environment..." -FilePath $python.Source -ArgumentList @("-m", "venv", (Join-Path $rootPath ".venv"))
        return
    }

    throw "Python was not found. Install Python 3, then run start-all.bat again."
}

function Ensure-BackendDependencies {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        New-GradeScopeVenv
    }

    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "Python virtual environment was not created at $venvPython."
    }

    if (-not (Test-Path -LiteralPath $requirementsPath)) {
        throw "Backend requirements file was not found: $requirementsPath"
    }

    Invoke-LoggedCommand -Label "Installing backend dependencies..." -FilePath $venvPython -ArgumentList @("-m", "pip", "install", "-r", $requirementsPath)
    Invoke-LoggedCommand -Label "Checking Playwright Chromium..." -FilePath $venvPython -ArgumentList @("-m", "playwright", "install", "chromium")
}

function Ensure-FrontendDependencies {
    $npm = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
    if (-not $npm) {
        $npm = Get-Command "npm.exe" -ErrorAction SilentlyContinue
    }

    if (-not $npm) {
        throw "npm was not found. Install Node.js LTS, then run start-all.bat again."
    }

    if (-not (Test-Path -LiteralPath $nodeModulesPath)) {
        Invoke-LoggedCommand -Label "Installing frontend dependencies..." -FilePath $npm.Source -ArgumentList @("install") -WorkingDirectory $frontendPath
    }
}

if (-not (Test-Path -LiteralPath $backendPath)) {
    throw "Backend folder not found: $backendPath"
}

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "Frontend folder not found: $frontendPath"
}

Ensure-BackendDependencies
Ensure-FrontendDependencies

$job = [IntPtr]::Zero
$processes = @()
$assignedProcessIds = @{}

try {
    $job = New-KillOnCloseJob

    $processes += Start-ManagedWindow -Job $job -Title "GradeScope Backend" -WorkingDirectory $backendPath -FilePath $venvPython -ArgumentList @("main.py")
    $processes += Start-ManagedWindow -Job $job -Title "GradeScope Frontend" -WorkingDirectory $frontendPath -FilePath "cmd.exe" -ArgumentList @("/d", "/s", "/c", "npm run dev")
    Add-ProcessTreeToJob -Job $job -RootProcessIds @($processes.Id) -AssignedProcessIds $assignedProcessIds

    Write-Host ""
    Write-Host "GradeScope is starting in two PowerShell windows."
    Write-Host "Backend:  http://127.0.0.1:8000"
    Write-Host "Frontend: http://127.0.0.1:5173"
    Write-Host ""
    Write-Host "Close this launcher, the backend window, or the frontend window to stop everything."
    Write-Host ""

    while ($true) {
        Start-Sleep -Milliseconds 500
        Add-ProcessTreeToJob -Job $job -RootProcessIds @($processes.Id) -AssignedProcessIds $assignedProcessIds
        foreach ($process in $processes) {
            if ($process.HasExited) {
                Write-Host "$($process.ProcessName) exited. Stopping all GradeScope processes..."
                return
            }
        }
    }
}
finally {
    Stop-TrackedProcesses -AssignedProcessIds $assignedProcessIds -RootProcessIds @($processes.Id)

    if ($job -ne [IntPtr]::Zero) {
        [JobApi]::CloseHandle($job) | Out-Null
    }

    foreach ($process in $processes) {
        if ($process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
}
