# Pre-filter the large norvig list once into a smaller clean file for faster builds.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

$stops = @('the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','day','get','has','him','his','how','man','new','now','old','see','two','way','who','boy','end','did','its','let','put','say','she','too','use','dad','mom','off','own','may','try','ask','big','per','act','set','yet','far','few','that','with','this','from','which','have','were','they','will','their','been','other','there','would','more','such','when','any','these','time','than','some','what','about','state','only','into','also','them','said','under','first','made','should','after','shall','your','most','could','then','over','each','year','work','where','years','between','those','same','many','through','upon','must','well','very','general','before','used','because','being','part','like','united','people','during','public','section','number','even','make','court','case','system','much','three','both','water','law','life','company','service','good','without','order','great','american','while','however','york','long','high','national','right','does','city','just','here','world','another','data','business','given','know','program','little','since','present','every','house','men','report','less','back','place','total','large','take','down','small','county','second','control','might','research','office','last','point','form','board','still','children','interest','federal','study','area','action','value','fact','line','found','power','states','within','school','against')

$cities = @{}
Get-Content 'cities/uk_cities.txt' -ErrorAction SilentlyContinue | ForEach-Object { $t = $_.ToLower().Trim(); if ($t) { $cities[$t] = $true } }
if (Test-Path 'cities/world-cities.csv') {
  Import-Csv 'cities/world-cities.csv' -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.name) { $n = $_.name.ToLower().Trim(); if ($n -match '^[a-z]{3,8}$') { $cities[$n] = $true } }
  }
}

$profs = @{}
Get-Content 'profanity.txt' -ErrorAction SilentlyContinue | ForEach-Object { $t = $_.ToLower().Trim(); if ($t -and $t.Length -ge 3 -and $t.Length -le 8) { $profs[$t] = $true } }

$acroList = @('aaa','abc','api','aws','cdn','cli','cpu','css','dns','faq','ftp','gpu','gui','html','http','https','ide','ios','ip','iso','jpg','json','jwt','lcd','led','mac','md5','mp3','mp4','npm','pdf','png','ram','rom','rss','sdk','sql','ssh','ssl','svg','tcp','udp','url','usb','utf','vpn','xml','yaml','yml','gif','wav','mov','avi','exe','zip','tar','rar','deb','rpm','apk','ipa','bin','dat','tmp','log','src','lib','dev','prod','test','ci','cd','pr','mr','ui','ux','ai','ml','llm','gpt','bert','rag','db','orm','mvc','spa','pwa','wasm','webgl','sftp','saml','oidc','csrf','xss','nosql','rtc','p2p','www','csv','md')
$acro = @{}
$acroList | ForEach-Object { $acro[$_] = $true }

function Test-Good([string]$w) {
  if (-not $w) { return $false }
  if ($w.Length -lt 3 -or $w.Length -gt 8) { return $false }
  if ($w -notmatch '^[a-z]+$') { return $false }
  if ($w -notmatch '[aeiou]') { return $false }
  if ($stops -contains $w) { return $false }
  if ($cities.ContainsKey($w)) { return $false }
  if ($profs.ContainsKey($w)) { return $false }
  if ($acro.ContainsKey($w)) { return $false }
  return $true
}

Write-Host "Pre-filtering norvig/norvig-words-filtered.txt ..."
$clean = Get-Content 'norvig/norvig-words-filtered.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } | Select-Object -Unique
Write-Host "Clean norvig words: $($clean.Count)"
$clean | Set-Content 'norvig/norvig_clean.txt' -Encoding utf8
Write-Host "Written norvig/norvig_clean.txt"
