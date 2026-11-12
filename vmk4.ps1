$ErrorActionPreference = 'Continue'
Set-Location 'D:\MiniMax Code Repos\Guitar Lessons'

function Extract-Crop($video, $outdir, $name, $t, $crop) {
    $w,$h,$x,$y = $crop.Split(':')
    $out = Join-Path $outdir "$name.png"
    & ffmpeg -y -v error -ss $t -i $video -frames:v 1 -vf "crop=$w`:$h`:$x`:$y" $out
}

$jobs = @(
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','pat','18','880:280:110:1270'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','strum','12.75','720:260:0:620'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','patverse','25','630:330:35:560'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','patchorus','39','630:330:35:560'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','pat','20','600:350:320:1135'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','chords','13','845:340:160:1310'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','pat','30','850:300:110:1340')
)

foreach ($j in $jobs) {
    New-Item -ItemType Directory -Force -Path $j[1] | Out-Null
    Extract-Crop $j[0] $j[1] $j[2] $j[3] $j[4]
}
Write-Output "EXTRACTED-ROUND4"
