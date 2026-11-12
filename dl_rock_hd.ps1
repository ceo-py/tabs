$ErrorActionPreference = 'Continue'
$ids = @('bYOD1FQ9sgc','dK27UjMr1UI','e-XedYIyKC0','tFfQAG50H2g')
foreach ($id in $ids) {
    $out = "dl/hd_$id.mp4"
    if (Test-Path $out) { Write-Output "SKIP $id"; continue }
    $ok = $false
    for ($try = 1; $try -le 5 -and -not $ok; $try++) {
        Write-Output "=== TRY $try $id ==="
        py -3.14 -m yt_dlp --no-warnings --extractor-args "youtube:player_client=android_creator" -f "299/137/best" --no-part -o $out "https://www.youtube.com/watch?v=$id" 2>&1 | Select-Object -Last 4
        if (Test-Path $out) { $ok = $true; Write-Output "OK $id" }
        else { Start-Sleep -Seconds 20 }
    }
    if (-not $ok) { Write-Output "FAIL $id" }
    Start-Sleep -Seconds 10
}
Write-Output "DONE"
