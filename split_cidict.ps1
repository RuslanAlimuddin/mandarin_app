$inputFile = "cidict_index.json"
$outDir    = "cidict_split"
$chunkSize = 3000   # jumlah entri per file kecil — kecilkan angka ini kalau masih kebesaran

New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

Write-Host "Membaca $inputFile ..."
$json = Get-Content $inputFile -Raw | ConvertFrom-Json

if ($json -is [System.Array]) {
    $total = $json.Count
    Write-Host "Terdeteksi ARRAY dengan $total entri"
    for ($i = 0; $i -lt $total; $i += $chunkSize) {
        $end = [int][Math]::Min($i + $chunkSize - 1, $total - 1)
        $part = $json[$i..$end]
        $num = [int]([Math]::Floor($i / $chunkSize)) + 1
        $numStr = "{0:D3}" -f $num
        $outFile = Join-Path $outDir ("cidict_part$numStr.json")
        $text = $part | ConvertTo-Json -Depth 20
        [System.IO.File]::WriteAllText($outFile, $text, $utf8NoBom)
        Write-Host "  -> $outFile ($($part.Count) entri)"
    }
} else {
    $keys = $json.PSObject.Properties.Name
    $total = $keys.Count
    Write-Host "Terdeteksi OBJEK/DICT dengan $total key"
    for ($i = 0; $i -lt $total; $i += $chunkSize) {
        $end = [int][Math]::Min($i + $chunkSize - 1, $total - 1)
        $partKeys = $keys[$i..$end]
        $partObj = [ordered]@{}
        foreach ($k in $partKeys) { $partObj[$k] = $json.$k }
        $num = [int]([Math]::Floor($i / $chunkSize)) + 1
        $numStr = "{0:D3}" -f $num
        $outFile = Join-Path $outDir ("cidict_part$numStr.json")
        $text = $partObj | ConvertTo-Json -Depth 20
        [System.IO.File]::WriteAllText($outFile, $text, $utf8NoBom)
        Write-Host "  -> $outFile ($($partKeys.Count) key)"
    }
}
Write-Host "SELESAI. File-file kecil ada di folder: $outDir"