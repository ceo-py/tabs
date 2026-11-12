$ErrorActionPreference = 'Continue'
Set-Location 'D:\MiniMax Code Repos\Guitar Lessons'

function Extract-Crop($video, $outdir, $name, $t, $crop) {
    $w,$h,$x,$y = $crop.Split(':')
    $out = Join-Path $outdir "$name.png"
    & ffmpeg -y -v error -ss $t -i $video -frames:v 1 -vf "crop=$w`:$h`:$x`:$y" $out
}

$jobs = @(
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','C','28','150:290:60:160'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','D7','32','150:290:60:160'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','G7','34','150:290:60:160'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','strum','12','700:170:190:1175'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','verse','27','540:420:270:930'),

  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','chords','1','720:275:190:128'),
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','strum','12','320:110:670:420'),
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','pat1','12','610:85:350:1155'),
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','pat2','12','610:80:350:1292'),

  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','chords','3','545:265:290:78'),
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','strum','45','385:235:690:325'),
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','pat','18','850:225:135:1315'),

  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','G','27','135:240:520:45'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','D','33','135:240:520:45'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','C','39','135:240:520:45'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','strum','12','720:235:0:650'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','patverse','25','630:240:35:585'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','patchorus','39','630:240:35:585'),

  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','chords','10','555:270:295:1325'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','strum','13','360:180:310:1370'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','pat','20','545:255:325:1170'),

  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','chords','3','490:270:305:118'),
  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','strum','9','300:120:685:408'),
  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','pat','9','740:310:50:1080'),

  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','chords','13','845:390:160:1355'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','strum','22','530:135:225:1405'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','pat','30','750:200:110:1360')
)

foreach ($j in $jobs) {
    New-Item -ItemType Directory -Force -Path $j[1] | Out-Null
    Extract-Crop $j[0] $j[1] $j[2] $j[3] $j[4]
}
Write-Output "EXTRACTED-ROUND2"
