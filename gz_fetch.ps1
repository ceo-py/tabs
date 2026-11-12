$ErrorActionPreference = 'Stop'
Set-Location 'D:\MiniMax Code Repos\Guitar Lessons'

$ids = Get-Content -Encoding utf8 gz_ids.txt | Where-Object { $_.Trim() -ne '' }
$workers = 6
$chunks = @()
for ($i = 0; $i -lt $workers; $i++) { $chunks += ,@() }
for ($i = 0; $i -lt $ids.Count; $i++) { $chunks[$i % $workers] += $ids[$i] }

for ($i = 0; $i -lt $workers; $i++) {
    ($chunks[$i] -join "`n") | Out-File -Encoding utf8 "gz_chunk_$i.txt"
}

$jobs = @()
for ($i = 0; $i -lt $workers; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($wdir, $idx)
        Set-Location $wdir
        $outFile = "gz_meta_part_$idx.jsonl"
        $errFile = "gz_err_part_$idx.log"
        & py -3.14 -m yt_dlp --batch-file "gz_chunk_$idx.txt" --skip-download --no-warnings `
            --extractor-args "youtube:player_client=android" --print-json 1> $outFile 2> $errFile
        return $LASTEXITCODE
    } -ArgumentList (Get-Location).Path, $i
}

$jobs | Wait-Job | Out-Null
$jobs | ForEach-Object { Write-Output "job $($_.Id) state=$($_.State) exit=$($_.ChildJobs[0].Output)" }
$jobs | Remove-Job -Force

$total = 0
foreach ($f in (Get-ChildItem gz_meta_part_*.jsonl | Sort-Object Name)) {
    $n = (Get-Content -Encoding utf8 $f.FullName | Where-Object { $_.Trim() -ne '' }).Count
    Write-Output "$($f.Name): $n"
    $total += $n
}
Write-Output "TOTAL_METADATA_LINES=$total"
Write-Output "--- errors ---"
foreach ($f in (Get-ChildItem gz_err_part_*.log | Sort-Object Name)) {
    $c = Get-Content -Encoding utf8 $f.FullName | Where-Object { $_.Trim() -ne '' }
    if ($c) { Write-Output "$($f.Name): $($c.Count) lines" } else { Write-Output "$($f.Name): 0" }
}
