$ErrorActionPreference = 'Continue'
Set-Location 'D:\MiniMax Code Repos\Guitar Lessons'

# args: <videoFile> <outDir> then triples: name|timestamp|crop W:H:X:Y
function Extract-Crop($video, $outdir, $name, $t, $crop) {
    $w,$h,$x,$y = $crop.Split(':')
    $out = Join-Path $outdir "$name.png"
    & ffmpeg -y -v error -ss $t -i $video -frames:v 1 -vf "crop=$w`:$h`:$x`:$y" $out
    return $out
}

$jobs = @(
  # --- Elvis
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','C','28','150:290:60:160'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','D7','32','150:290:60:160'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','G7','34','150:290:60:160'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','strum','12','720:150:190:1130'),
  @('dl/v_vqZuzVZgHW8.mp4','frames/c_elvis','verse','27','540:420:270:930'),
  # --- Country Roads
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','chords','1','700:270:195:130'),
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','strum','12','300:80:675:440'),
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','pat1','12','610:70:350:1170'),
  @('dl/v_2_Bc3Pb-BYw.mp4','frames/c_cr','pat2','12','610:70:350:1298'),
  # --- Johnny Cash
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','chords','3','500:260:295:85'),
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','strum','45','380:170:690:345'),
  @('dl/v_gQXGVDNC-ic.mp4','frames/c_jc','pat','18','700:180:280:1330'),
  # --- Yellow 2023
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','G','27','130:230:525:55'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','D','33','130:230:525:55'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','C','39','130:230:525:55'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','strum','12','520:200:170:680'),
  @('dl/w_v_dYdX16QX84c.mp4','frames/c_y23','pat','27','560:80:95:580'),
  # --- Yellow 2023b
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','chords','9','510:370:290:1265'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','strum','12','540:110:330:1400'),
  @('dl/v_Jo4tMXg6wmI.mp4','frames/c_y23b','pat','21','960:250:95:1085'),
  # --- Yellow 2024
  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','chords','3','610:330:265:90'),
  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','strum','9','330:95:600:405'),
  @('dl/v_4TnTv2t5dQU.mp4','frames/c_y24','pat','21','960:250:95:1085'),
  # --- CCR
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','chords','12','820:410:150:1265'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','strum','21','500:110:130:1430'),
  @('dl/w_v_olBBttZ9dxk.mp4','frames/c_ccr','pat','30','520:190:130:1360')
)

foreach ($j in $jobs) {
    New-Item -ItemType Directory -Force -Path $j[1] | Out-Null
    Extract-Crop $j[0] $j[1] $j[2] $j[3] $j[4]
}
Write-Output "EXTRACTED"
