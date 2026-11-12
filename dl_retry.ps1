$ErrorActionPreference = 'Continue'
$env:Path = "$PWD\denobin;$env:Path"

$ids = @(
  '9pH9cccg6t8',   # We're Going To Be Friends - White Stripes (long)
  'bYOD1FQ9sgc',   # Have You Ever Seen the Rain (long)
  'dK27UjMr1UI',   # Bad Moon Rising - CCR Challenge (long)
  'e-XedYIyKC0',   # Proud Mary (long)
  'tFfQAG50H2g',   # Down on the Corner (long)
  'yRApqkc050s',   # Last Kiss - Pearl Jam (short)
  'dYdX16QX84c',   # Yellow (short)
  'olBBttZ9dxk',   # Have You Ever Seen the Rain (short)
  'qrtWlngUm0c',   # Viva La Vida (short)
  'O-sPPp1Qbbc'    # Bad Moon Rising jam-along (short)
)

foreach ($id in $ids) {
  if (Test-Path "dl/v_$id.mp4") { Write-Output "SKIP $id"; continue }
  $ok = $false
  for ($try = 1; $try -le 4 -and -not $ok; $try++) {
    py -3.14 -m yt_dlp --no-warnings --extractor-args "youtube:player_client=android_creator" -f "137/best" --no-part -o "dl/v_$id.%(ext)s" "https://www.youtube.com/watch?v=$id" 2>&1 | Select-Object -Last 1 | Out-Null
    if (Test-Path "dl/v_$id.mp4") { $ok = $true }
    else { Start-Sleep -Seconds (8 * $try) }
  }
  if ($ok) {
    $sz = [math]::Round((Get-Item "dl/v_$id.mp4").Length / 1MB, 1)
    Write-Output "OK $id  ${sz}MB"
  } else {
    Write-Output "FAIL $id"
  }
  Start-Sleep -Seconds 4
}
Write-Output "DONE"
