$ErrorActionPreference = 'Continue'
Set-Location 'D:\MiniMax Code Repos\Guitar Lessons'

function Extract-Crop($video, $outdir, $name, $t, $crop) {
    $w,$h,$x,$y = $crop.Split(':')
    $out = Join-Path $outdir "$name.png"
    & ffmpeg -y -v error -ss $t -i $video -frames:v 1 -vf "crop=$w`:$h`:$x`:$y" $out
}

$jobs = @(
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','strum','12','700:150:190:1210'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','verse','27','500:420:285:930'),

  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','strum','45','385:310:690:320'),
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','pat','18','880:250:110:1295'),

  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','strum','13','720:235:0:650'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','strum14','14','720:235:0:650'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','patverse','25','630:275:35:565'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','patchorus','39','630:275:35:565'),

  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','chords','10','555:320:295:1300'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','strum','13','420:180:300:1370'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','pat','20','600:340:320:1150'),

  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','pat','9','740:340:50:1055'),

  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','chords','13','845:460:160:1320'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','strum','22','580:140:215:1395'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','pat','30','850:210:110:1345')
)

foreach ($j in $jobs) {
    New-Item -ItemType Directory -Force -Path $j[1] | Out-Null
    Extract-Crop $j[0] $j[1] $j[2] $j[3] $j[4]
}
Write-Output "EXTRACTED-ROUND3"
