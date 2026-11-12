$ErrorActionPreference = 'Continue'
$env:Path = "$PWD\denobin;$env:Path"

$ids = @('bYOD1FQ9sgc', 'dK27UjMr1UI', 'dYdX16QX84c', 'olBBttZ9dxk', 'e-XedYIyKC0', 'tFfQAG50H2g', 'yRApqkc050s', 'qrtWlngUm0c', 'O-sPPp1Qbbc')

foreach ($id in $ids) {
  $existing = "dl/v_$id.mp4"
  $need = $true
  if (Test-Path $existing) {
    $wh = (ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 $existing 2>$null)
    $w = [int](($wh -split ',')[0]); $h = [int](($wh -split ',')[1])
    if ($w -ge 1000 -or ($h -ge 1000)) { $need = $false }
  }
  if (-not $need) { Write-Output "SKIP $id (already high-res)"; continue }

  for ($try = 1; $try -le 6; $try++) {
    py -3.14 -m yt_dlp --no-warnings --extractor-args "youtube:player_client=android_creator" -f "137/299/best" --no-part -o "dl/hi_$id.%(ext)s" "https://www.youtube.com/watch?v=$id" 2>&1 | Select-Object -Last 1 | Out-Null
    if (Test-Path "dl/hi_$id.mp4") {
      $wh = (ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "dl/hi_$id.mp4" 2>$null)
      $w = [int](($wh -split ',')[0]); $h = [int](($wh -split ',')[1])
      if ($w -ge 1000 -or $h -ge 1000) {
        Write-Output "HI $id  ${w}x${h}"
        break
      }
    }
    Start-Sleep -Seconds (6 * $try)
  }
  if (-not (Test-Path "dl/hi_$id.mp4")) { Write-Output "HI-FAIL $id" }
  Start-Sleep -Seconds 3
}
Write-Output "DONE"
