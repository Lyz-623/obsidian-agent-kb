# Render the README images from the vault's own code and CSS with headless Microsoft Edge.
#
#   powershell -ExecutionPolicy Bypass -File docs\preview\shoot.ps1
#
# 1. build_data.py indexes the notes into data.js;
# 2. headless Edge screenshots home.html (the real 90 System/home/view.js on a Dataview stand-in) and
#    note.html (notes rendered with markdown-it + KaTeX and the vault's kb-article.css);
# 3. trim.py cuts the empty background below the content; graph.py draws the link graph.
# Output: docs/images/home-light.png, term.png, graph.png. Other views, e.g. dark mode or an article excerpt,
# can be rendered the same way (home.html?theme=dark, note.html?n=<path>&at=<heading or block id>).
# The real Obsidian screenshots docs/images/obsidian-*.png are never touched by this script.
# Needs Python 3 (Pillow for trimming, matplotlib for the graph) and network access to cdn.jsdelivr.net.
param(
  [string]$Edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
  [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$repo = (Resolve-Path (Join-Path $here '..\..')).Path
$images = Join-Path $repo 'docs\images'
New-Item -ItemType Directory -Force $images | Out-Null
if (-not (Test-Path $Edge)) { throw "Edge not found: $Edge" }

& $Python (Join-Path $here 'build_data.py')
if ($LASTEXITCODE -ne 0) { throw 'build_data.py failed' }

$profileDir = Join-Path ([IO.Path]::GetTempPath()) ('kb-preview-' + [guid]::NewGuid().ToString('N'))

function Get-FileUrl([string]$page, [hashtable]$query) {
  $path = (Join-Path $here $page) -replace '\\', '/'
  $segments = ($path -split '/') | ForEach-Object { [uri]::EscapeDataString($_) -replace '%3A', ':' }
  $url = 'file:///' + ($segments -join '/')
  if ($query -and $query.Count) {
    $pairs = $query.GetEnumerator() | Sort-Object Name | ForEach-Object { $_.Name + '=' + [uri]::EscapeDataString($_.Value) }
    $url += '?' + ($pairs -join '&')
  }
  return $url
}

function Save-Shot([string]$page, [hashtable]$query, [int]$width, [int]$height, [string]$name) {
  $out = Join-Path $images $name
  if (Test-Path $out) { Remove-Item $out -Force }
  $url = Get-FileUrl $page $query
  # Start-Process joins the arguments with spaces, so paths that may contain spaces are quoted.
  $edgeArgs = @('--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
            "--user-data-dir=`"$profileDir`"", '--virtual-time-budget=8000', '--force-device-scale-factor=1',
            "--window-size=$width,$height", "--screenshot=`"$out`"", $url)
  Start-Process -FilePath $Edge -ArgumentList $edgeArgs -Wait -WindowStyle Hidden
  if (-not (Test-Path $out)) { throw "no screenshot written for $name" }
  Write-Host "shot $name  <- $url"
}

try {
  Save-Shot 'home.html' @{} 1400 1300 'home-light.png'
  Save-Shot 'note.html' @{ n = '30 Terms/Quality factor.md' } 1100 760 'term.png'
} finally {
  if (Test-Path $profileDir) { Remove-Item $profileDir -Recurse -Force -ErrorAction SilentlyContinue }
}

& $Python (Join-Path $here 'trim.py') (Join-Path $images 'home-light.png') (Join-Path $images 'term.png')
& $Python (Join-Path $here 'graph.py')
if ($LASTEXITCODE -ne 0) { throw 'graph.py failed' }
Get-ChildItem $images -Filter *.png | Where-Object { $_.Name -notlike 'obsidian-*' } | ForEach-Object { '{0,-16} {1,6} KB' -f $_.Name, [math]::Round($_.Length / 1KB) }
