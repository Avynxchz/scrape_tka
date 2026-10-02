# ============================================================
# BAGIKAN ONLINE — ekspos app lokal ke internet via tunnel.
# Pakai: cloudflared (tanpa akun, default) atau ngrok (-Tunnel ngrok).
# Server demo berjalan di port 8081 dengan PUBLIC_DEMO=1
# (endpoint admin dimatikan otomatis).
# Matikan: jalankan matikan_bagikan.bat, atau Ctrl+C di jendela ini.
# Catatan: crawler AI (mis. Claude) diblokir robots.txt milik Cloudflare di
# domain trycloudflare.com — untuk audit oleh AI, pakai -Tunnel ngrok.
# ============================================================
param([string]$Tunnel = "cloudflared")
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$port = 8081
$tunnel = $null

if (-not (Test-Path "scratch")) { New-Item -ItemType Directory -Path "scratch" | Out-Null }

# --- 1. Pastikan cloudflared tersedia (unduh jika belum ada) ---
if (-not (Test-Path ".\cloudflared.exe")) {
    Write-Host "[1/4] Mengunduh cloudflared (~55 MB, sekali saja)..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile ".\cloudflared.exe" -UseBasicParsing
    } catch {
        Write-Host "Gagal mengunduh cloudflared: $_" -ForegroundColor Red
        Write-Host "Coba jalankan: ngrok http $port  (butuh akun ngrok)"
        pause
        exit 1
    }
} else {
    Write-Host "[1/4] cloudflared sudah ada." -ForegroundColor Green
}

# --- 2. Nyalakan server demo di port 8081 (PUBLIC_DEMO=1) ---
Write-Host "[2/4] Menyalakan server demo di port $port (mode publik, admin API off)..." -ForegroundColor Cyan
$env:PORT = "$port"
$env:PUBLIC_DEMO = "1"
$server = Start-Process -FilePath "python" -ArgumentList "server.py" `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$PSScriptRoot\scratch\demo_server.log" `
    -RedirectStandardError  "$PSScriptRoot\scratch\demo_server_err.log" `
    -PassThru

$up = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $r = Invoke-WebRequest "http://127.0.0.1:$port/" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $up = $true; break }
    } catch { }
}
if (-not $up) {
    Write-Host "Server gagal hidup. Cek scratch\demo_server_err.log" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "      Server demo hidup (PID $($server.Id))." -ForegroundColor Green

# --- 3. Nyalakan tunnel ---
$url = $null
$cf = $null
$ng = $null

# 3a. cloudflared (tanpa akun) — dilewati bila -Tunnel ngrok
if ($Tunnel -ne "ngrok") {
    Write-Host "[3/4] Menyalakan tunnel cloudflared..." -ForegroundColor Cyan
    if (Test-Path "scratch\tunnel.log") { Remove-Item "scratch\tunnel.log" -Force -ErrorAction SilentlyContinue }
    $cf = Start-Process -FilePath ".\cloudflared.exe" `
        -ArgumentList "tunnel", "--url", "http://127.0.0.1:$port", "--logfile", "$PSScriptRoot\scratch\tunnel.log" `
        -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru

    for ($i = 0; $i -lt 45; $i++) {
        Start-Sleep -Seconds 1
        if ($cf.HasExited) { break }
        if (Test-Path "scratch\tunnel.log") {
            $m = Select-String -Path "scratch\tunnel.log" -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($m) { $url = $m.Matches[0].Value; $tunnel = "cloudflared"; break }
        }
    }
}

# 3b. Fallback: ngrok (sudah terinstall & terauth di mesin ini)
if (-not $url) {
    Write-Host "      cloudflared gagal, mencoba ngrok..." -ForegroundColor Yellow
    if ($cf -and -not $cf.HasExited) { Stop-Process -Id $cf.Id -Force -ErrorAction SilentlyContinue }
    if (Test-Path "scratch\tunnel_ngrok.log") { Remove-Item "scratch\tunnel_ngrok.log" -Force -ErrorAction SilentlyContinue }
    $ng = Start-Process -FilePath "ngrok" `
        -ArgumentList "http", "$port", "--log", "$PSScriptRoot\scratch\tunnel_ngrok.log", "--log-format", "json" `
        -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if ($ng.HasExited) { break }
        try {
            $api = Invoke-RestMethod "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 2
            $u = $api.tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1
            if ($u) { $url = $u.public_url; $tunnel = "ngrok"; break }
        } catch { }
    }
}

if (-not $url) {
    Write-Host "GAGAL mendapatkan URL tunnel. Cek scratch\tunnel.log / tunnel_ngrok.log" -ForegroundColor Red
    Write-Host "Kemungkinan: tidak ada internet, atau kuota tunnel sedang bermasalah."
    if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue }
    pause
    exit 1
}

Write-Host "[4/4] Siap!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "  LINK UNTUK DIBAGIKAN ($tunnel):" -ForegroundColor Yellow
Write-Host "     $url" -ForegroundColor White
Write-Host "" -ForegroundColor Yellow
Write-Host "  Biarkan jendela ini tetap terbuka selama dibagikan." -ForegroundColor Yellow
Write-Host "  Tekan Ctrl+C di sini ATAU jalankan matikan_bagikan.bat" -ForegroundColor Yellow
Write-Host "  untuk mematikan." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# Catat URL agar mudah dilihat lagi
Set-Content -Path "scratch\tunnel_url.txt" -Value $url

# Tetap hidup selama tunnel berjalan; Ctrl+C akan melewati finally.
try {
    if ($cf -and -not $cf.HasExited) { Wait-Process -Id $cf.Id -ErrorAction SilentlyContinue }
    elseif ($ng -and -not $ng.HasExited) { Wait-Process -Id $ng.Id -ErrorAction SilentlyContinue }
    else { while ($true) { Start-Sleep -Seconds 5 } }
} finally {
    Write-Host "Mematikan tunnel & server demo..." -ForegroundColor Cyan
    if ($cf -and -not $cf.HasExited) { Stop-Process -Id $cf.Id -Force -ErrorAction SilentlyContinue }
    if ($ng -and -not $ng.HasExited) { Stop-Process -Id $ng.Id -Force -ErrorAction SilentlyContinue }
    if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue }
    Write-Host "Selesai. Semua dimatikan."
}
