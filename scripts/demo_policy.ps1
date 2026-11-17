#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Tmp = Join-Path $Root "reports\demo"
New-Item -ItemType Directory -Path $Tmp -Force | Out-Null

python -m pip install -e . -q
python -m policy_gate status

$dry = Join-Path $Tmp "dry_spot.json"
$fut = Join-Path $Tmp "futures.json"
$live = Join-Path $Tmp "live_nokeys.json"

function Write-Utf8NoBom([string]$Path, [string]$Text) {
  $utf8 = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($Path, $Text, $utf8)
}
Write-Utf8NoBom $dry '{"symbol":"BTCUSDT","side":"buy","market":"spot","sector":"spot_alts","quote_usdt_micros":1000000,"dry_run":true}'
Write-Utf8NoBom $fut '{"symbol":"BTCUSDT","side":"buy","market":"futures","dry_run":true}'
Write-Utf8NoBom $live '{"symbol":"BTCUSDT","side":"buy","market":"spot","dry_run":false,"ops_ready":true}'


Write-Host "`n== dry spot (expect ALLOW) =="
python -m policy_gate evaluate --file $dry --assume-keys no --audit
Write-Host "exit=$LASTEXITCODE"

Write-Host "`n== futures (expect REFUSE) =="
python -m policy_gate evaluate --file $fut --assume-keys no
Write-Host "exit=$LASTEXITCODE"

Write-Host "`n== live without keys (expect REFUSE) =="
python -m policy_gate evaluate --file $live --assume-keys no
Write-Host "exit=$LASTEXITCODE"
exit 0
