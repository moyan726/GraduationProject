Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-CondaLoaded {
  if (Get-Command conda -ErrorAction SilentlyContinue) { return }
  $condaHook = Join-Path $env:USERPROFILE "anaconda3\shell\condabin\conda-hook.ps1"
  if (Test-Path $condaHook) {
    . $condaHook
    return
  }
  throw "conda 命令不可用。请先安装 Anaconda/Miniconda，或在 PowerShell 中初始化 conda。"
}

Ensure-CondaLoaded

conda activate graduation_project

$env:JAVA_HOME = "E:\Java\jdk1.8.0_291"
$env:PYSPARK_PYTHON = (Get-Command python).Source
$env:PYSPARK_DRIVER_PYTHON = $env:PYSPARK_PYTHON

Write-Host "已进入隔离环境：graduation_project"
Write-Host "JAVA_HOME=$env:JAVA_HOME"
Write-Host "PYSPARK_PYTHON=$env:PYSPARK_PYTHON"
