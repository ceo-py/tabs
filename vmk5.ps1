$ErrorActionPreference = 'Continue'
Set-Location 'D:\MiniMax Code Repos\Guitar Lessons'

function Extract-Crop($video, $outdir, $name, $t, $crop) {
    $w,$h,$x,$y = $crop.Split(':')
    $out = Join-Path $outdir "$name.png"
    & ffmpeg -y -v error -ss $t -i $video -frames:v 1 -vf "crop=$w`:$h`:$x`:$y" $out
}

$jobs = @(
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','strum','12','320:70:670:450'),
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','strum','45','385:290:690:340'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','chords','10','590:320:270:1300'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','strum','13','470:180:300:1370'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','pat','20','600:380:320:1135'),
  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','pat','9','800:340:50:1055')
)

foreach ($j in $jobs) {
    Extract-Crop $j[0] $j[1] $j[2] $j[3] $j[4]
}
Write-Output "EXTRACTED-ROUND5"
