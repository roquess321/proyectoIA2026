$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# 1. Localizar binario de cloudflared
$CloudflaredCmd = Get-Command cloudflared -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1
if (-not $CloudflaredCmd) {
    $LocalCloudflared = Join-Path $env:LOCALAPPDATA 'cloudflared\cloudflared.exe'
    if (Test-Path $LocalCloudflared) {
        $CloudflaredCmd = $LocalCloudflared
    }
}

if (-not $CloudflaredCmd) {
    Write-Host '❌ No se encontró cloudflared en PATH ni en %LOCALAPPDATA%\cloudflared\cloudflared.exe.' -ForegroundColor Red
    Write-Host 'Descarga oficial Windows x64:' -ForegroundColor Yellow
    Write-Host '  New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\cloudflared" | Out-Null' -ForegroundColor Gray
    Write-Host '  Invoke-WebRequest "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "$env:LOCALAPPDATA\cloudflared\cloudflared.exe"' -ForegroundColor Gray
    exit 1
}

function Test-BackendOnline {
    try {
        $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 2
        return ($resp.StatusCode -eq 200)
    } catch {
        return $false
    }
}

$StartedBackendProc = $null
try {
    # 2. Iniciar backend FastAPI si el puerto 8000 aún no responde
    if (Test-BackendOnline) {
        Write-Host '✅ Backend FastAPI ya se encuentra activo en http://127.0.0.1:8000' -ForegroundColor Green
    } else {
        Write-Host '🚀 Iniciando servidor backend FastAPI en http://127.0.0.1:8000...' -ForegroundColor Cyan
        $StartedBackendProc = Start-Process -FilePath 'uv' -ArgumentList @('run', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Minimized

        $ready = $false
        for ($i = 0; $i -lt 45; $i++) {
            Start-Sleep -Seconds 1
            if (Test-BackendOnline) {
                $ready = $true
                break
            }
            if ($StartedBackendProc.HasExited) {
                throw "El proceso backend terminó inesperadamente (código $($StartedBackendProc.ExitCode))."
            }
        }

        if (-not $ready) {
            throw 'El backend FastAPI no respondió a tiempo en http://127.0.0.1:8000/.'
        }
        Write-Host '✅ Backend FastAPI listo (200 OK).' -ForegroundColor Green
    }

    # 3. Iniciar Quick Tunnel de Cloudflare y resaltar URL pública + enlace directo Vercel
    Write-Host '🌐 Abriendo túnel HTTPS Cloudflare hacia http://127.0.0.1:8000...' -ForegroundColor Cyan
    Write-Host '   Presiona Ctrl+C para detener el túnel al finalizar la defensa.' -ForegroundColor DarkGray

    $UrlShown = $false
    & $CloudflaredCmd tunnel --url http://127.0.0.1:8000 2>&1 | ForEach-Object {
        $line = $_.ToString()
        Write-Host $line
        if (-not $UrlShown -and $line -match 'https://[a-z0-9-]+\.trycloudflare\.com') {
            $TunnelUrl = $Matches[0]
            $UrlShown = $true
            Write-Host ''
            Write-Host '========================================================================' -ForegroundColor Green
            Write-Host "  Túnel HTTPS activo : $TunnelUrl" -ForegroundColor Green
            Write-Host "  Abrir en Vercel    : https://fiunai-helper.vercel.app/?api=$TunnelUrl" -ForegroundColor Cyan
            Write-Host '========================================================================' -ForegroundColor Green
            Write-Host ''
        }
    }
} finally {
    if ($StartedBackendProc -and -not $StartedBackendProc.HasExited) {
        Write-Host '🛑 Deteniendo servidor backend iniciado por este script...' -ForegroundColor Yellow
        Stop-Process -Id $StartedBackendProc.Id -Force -ErrorAction SilentlyContinue
    }
}
