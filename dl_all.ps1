$ErrorActionPreference = 'Continue'
$env:Path = "$PWD\denobin;$env:Path"

$ids = @(
  'M8rVBAJhcLI',   # Bad Moon Rising - EASY CHORDS (long)
  'MfIguC1c2hQ',   # Yellow by Coldplay (long)
  '9pH9cccg6t8',   # We're Going To Be Friends - White Stripes (long)
  'bYOD1FQ9sgc',   # Have You Ever Seen the Rain (long)
  'dK27UjMr1UI',   # Bad Moon Rising - CCR Challenge (long)
  'e-XedYIyKC0',   # Proud Mary (long)
  'tFfQAG50H2g',   # Down on the Corner (long)
  'yRApqkc050s',   # Last Kiss - Pearl Jam (short)
  'dYdX16QX84c',   # Yellow (short)
  'vqZuzVZgHW8',   # Love Me Tender - Elvis (short)
  'olBBttZ9dxk',   # Have You Ever Seen the Rain (short)
  'Jo4tMXg6wmI',   # Yellow (short 2)
  'qrtWlngUm0c',   # Viva La Vida (short)
  'O-sPPp1Qbbc',   # Bad Moon Rising jam-along (short)
  'VAiS4VW7Eyc',   # Hotel California (short)
  'PInjnaAQ54Y',   # Crazy Little Thing Called Love - Queen (short)
  '2_Bc3Pb-BYw',   # Take Me Home Country Roads (short)
  'gQXGVDNC-ic',   # I Walk The Line (short)
  '4TnTv2t5dQU',   # Yellow (short 3)
  'KIFZsklFIfE'    # Losing My Religion - R.E.M. (short)
)

New-Item -ItemType Directory -Force -Path dl | Out-Null
foreach ($id in $ids) {
  $out = "dl/v_$id.%(ext)s"
  if (Test-Path "dl/v_$id.mp4") { Write-Output "SKIP $id"; continue }
  py -3.14 -m yt_dlp --no-warnings --extractor-args "youtube:player_client=android_creator" -f "137/best" --no-part -o $out "https://www.youtube.com/watch?v=$id" 2>&1 | Select-Object -Last 1 | Out-Null
  if (Test-Path "dl/v_$id.mp4") {
    $sz = [math]::Round((Get-Item "dl/v_$id.mp4").Length / 1MB, 1)
    Write-Output "OK $id  ${sz}MB"
  } else {
    Write-Output "FAIL $id"
  }
}
Write-Output "DONE"
