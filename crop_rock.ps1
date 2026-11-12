$ErrorActionPreference = 'Continue'
$w = 'D:\MiniMax Code Repos\Guitar Lessons'
$FR = "$w\frames"

function CropV($video, $t, $out, $cw, $ch, $cx, $cy) {
    ffmpeg -y -v error -ss $t -i $video -frames:v 1 -vf "crop=$cw`:$ch`:$cx`:$cy" $out
}

# ============ bYOD1FQ9sgc : Have You Ever Seen the Rain ============
$v = "$w\dl\hd_bYOD1FQ9sgc.mp4"; $d = "$FR\rock_bYOD1FQ9sgc"
CropV $v 225 "$d\c_chord_Am.png" 125 225 1750 50
CropV $v 225 "$d\c_chord_C.png"  125 210 1750 290
CropV $v 225 "$d\c_chord_G.png"  125 210 1750 535
CropV $v 225 "$d\c_chord_F.png"  125 205 1750 785
CropV $v 225 "$d\c_strum_main.png"  250 120 25 30
CropV $v 100 "$d\c_strum_intro.png" 215 120 25 30
CropV $v 325 "$d\c_pattern_verse1.png" 1250 145 25 860
CropV $v 450 "$d\c_pattern_verse2.png" 1250 145 25 860
CropV $v 650 "$d\c_pattern_chorus.png" 1250 145 25 860
CropV $v 850 "$d\c_pattern_bridge.png" 1250 145 25 860

# ============ dK27UjMr1UI : Bad Moon Rising (CCR Challenge 2) ============
$v = "$w\dl\hd_dK27UjMr1UI.mp4"; $d = "$FR\rock_dK27UjMr1UI"
CropV $v 450 "$d\c_chord_D.png" 125 235 1750 60
CropV $v 450 "$d\c_chord_A.png" 125 235 1750 340
CropV $v 450 "$d\c_chord_G.png" 125 245 1750 610
CropV $v 450 "$d\c_strum.png"      390 610 25 30
CropV $v 250 "$d\c_pattern_verse.png"  780 215 25 865
CropV $v 450 "$d\c_pattern_chorus.png" 1350 215 25 865

# ============ e-XedYIyKC0 : Proud Mary (CCR Challenge 3) ============
$v = "$w\dl\hd_e-XedYIyKC0.mp4"; $d = "$FR\rock_e-XedYIyKC0"
CropV $v 300 "$d\c_chord_D.png"  125 235 1750 60
CropV $v 300 "$d\c_chord_A.png"  125 235 1750 340
CropV $v 300 "$d\c_chord_Bm.png" 125 240 1750 640
CropV $v 25  "$d\c_strum_options.png" 460 130 30 30
CropV $v 250 "$d\c_chuck.png"          410 145 30 30
CropV $v 400 "$d\c_bm_trans.png"       420 130 30 30
CropV $v 775 "$d\c_intro_panel.png"    330 880 0 25
CropV $v 775 "$d\c_pattern_intro.png" 1030  95 445 960

# ============ tFfQAG50H2g : Down on the Corner (CCR Challenge) ============
$v = "$w\dl\hd_tFfQAG50H2g.mp4"; $d = "$FR\rock_tFfQAG50H2g"
CropV $v 650 "$d\c_chord_C.png" 85 175 45 15
CropV $v 650 "$d\c_chord_G.png" 85 140 45 205
CropV $v 650 "$d\c_chord_F.png" 85 170 45 390
CropV $v 600 "$d\c_strum_option.png" 255 82 1010 8
CropV $v 100 "$d\c_strum_count.png"  255 112 1010 8
CropV $v 650 "$d\c_pattern_intro.png" 1045 170 185 525
CropV $v 600 "$d\c_pattern_verse.png" 1045 170 185 525
CropV $v 1075 "$d\c_tab_bass.png"     600 165 185 530

# extra bYOD bar strip (later sections)
foreach ($t in @(700,750,800,900,1000,1100)) { CropV "$w\dl\hd_bYOD1FQ9sgc.mp4" $t "$FR\rock_bYOD1FQ9sgc\bar2_$t.png" 1920 150 0 855 }
py -3.14 "$w\stack_rock.py" "$FR\rock_bYOD1FQ9sgc\bars_late.png" "$FR\rock_bYOD1FQ9sgc\bar2_700.png" "$FR\rock_bYOD1FQ9sgc\bar2_750.png" "$FR\rock_bYOD1FQ9sgc\bar2_800.png" "$FR\rock_bYOD1FQ9sgc\bar2_900.png" "$FR\rock_bYOD1FQ9sgc\bar2_1000.png" "$FR\rock_bYOD1FQ9sgc\bar2_1100.png"
Write-Output 'CROPS DONE'
