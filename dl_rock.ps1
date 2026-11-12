$ErrorActionPreference = 'Continue'
$ids = @('9pH9cccg6t8','bYOD1FQ9sgc','dK27UjMr1UI','e-XedYIyKC0','tFfQAG50H2g')
foreach ($id in $ids) {
    $out = "dl/v_$id.mp4"
    if (Test-Path $out) { Write-Output "SKIP $id (exists)"; continue }
    $ok = $false
    for ($try = 1; $try -le 4 -and -not $ok; $try++) {
        Write-Output "=== TRY $try $id ==="
        if ($try -eq 1) {
            $ea = 'youtube:player_client=android_creator'
        } else {
            $ea = 'youtube:player_client=android'
        }
        py -3.14 -m yt_dlp --no-warnings --extractor-args $ea -f "137/best" --no-part -o $out "https://www.youtube.com/watch?v=$id" 2>&1 | Select-Object -Last 6
        if (Test-Path $out) { $ok = $true; Write-Output "OK $id" }
        else { Start-Sleep -Seconds 15 }
    }
    if (-not $ok) { Write-Output "FAIL $id" }
    Start-Sleep -Seconds 12
}
Write-Output "DONE"
