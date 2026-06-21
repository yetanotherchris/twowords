param()
$ErrorActionPreference = 'Stop'
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $base) { $base = Get-Location }
Set-Location $base

$required = 64434

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

Write-Host "Loading sources (relative to v2/)..."

$kag = @()
if (Test-Path 'kaggle/common_clean.txt') { 
  $kag = Get-Content 'kaggle/common_clean.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } 
  Write-Host "  kaggle: $($kag.Count)"
}

$foods = @()
if (Test-Path 'claude/food_dishes_final.txt') { 
  $foods = Get-Content 'claude/food_dishes_final.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } 
  Write-Host "  foods: $($foods.Count)"
}

$convRaw = @('wifi','bluetooth','yapping','yap','meme','vibe','vibes','ghost','flex','troll','spam','ping','zoom','tweet','post','like','share','stream','chat','app','bug','crash','sync','cache','cloud','login','logout','update','swipe','scroll','tap','click','drag','drop','snap','selfie','story','reel','clip','filter','hashtag','emoji','gif','mood','cringe','sus','cap','bet','slay','lit','fire','dope','sick','yeet','rizz','skibidi','sigma','gyatt','delulu','bruh','drip','glow','hype','fomo','jomo','stan','shade','salty','savage','roast','burn','clapback','ratio','mid','bussin','cheugy','main','character','npc','alpha','beta','omega','goat','based','cope','seethe','lfg','dub','sheesh','fr','frfr','ong','pog','poggers','kek','kekw','lul','lmao','lmfao','rofl','af','asf','iykyk','fyi','tldr','imo','imho','idk','idc','smh','facepalm','wtf','wth','brb','afk','irl','fwiw','nsfw','sfw','ama','eli5','op','yolo','tiktok','insta','snapchat','reddit','discord','slack','teams','meet','skype','facetime','airdrop','airplay','hotspot','vpn','dns','ip','mac','gui','cli','api','sdk','ide','fix','patch','release','deploy','commit','push','pull','merge','branch','fork','clone','repo','git','npm','yarn','pip','cargo','docker','pod','helm','aws','gcp','azure','lambda','s3','cdn','ssl','tls','http','https','tcp','udp','ssh','ftp','jwt','oauth','sql','nosql','db','orm','react','vue','svelte','angular','astro','next','nuxt','vite','webpack','babel','ts','js','jsx','tsx','css','scss','sass','html','xml','json','yaml','yml','toml','md','csv','log','kafka','rabbit','redis','spark','flink','node','python','rust','java','kotlin','swift','go','ruby','php','shell','bash','zsh','fish','make','cmake','gradle','maven','nginx','haproxy','fastapi','flask','django','rails','spring','express','laravel','electron','flutter','ios','android','linux','macos','windows','unix','async','await','promise','thread','lock','queue','stack','heap','array','list','map','set','hash','tree','graph','vector','matrix','token','embed','prompt','agent','tool','chunk','index','faiss','duckdb','pandas','numpy','torch','jax','keras','llm','gpt','bert','diffusion','stable','genai','rag','ml','ai','web','net','site','link','feed','live','text','dm','tag','heart','save','view','play','pause','stop','skip','search','find','open','close','edit','delete','add','hot','cold','fast','slow','good','bad','nice','cool','fun','sad','happy','mad','tired','bored','busy','free','easy','hard','simple','clean','fresh','sweet','sour','spicy','loud','quiet','bright','dark','light','heavy','soft','wet','dry','warm','young','rich','poor','high','low','long','short','wide','deep','full','empty','true','false','yes','no','ok','fine','great','best','worst','first','last','next','top','bottom','left','right','center','front','back','edge','line','point','icon','image','photo','pic','video','audio','sound','music','song','beat','voice','talk','speak','say','tell','ask','answer','question','reply','comment','status','broadcast','podcast','radio','tv','netflix','youtube','messenger','webrtc','p2p','mesh','server','client','host','backup','restore','upgrade','install','uninstall','download','upload','cookie','session','signup','signin','auth','secret','password','pass','pin','encrypt','decrypt','hash','sign','verify','cert','proxy','firewall','router','switch','modem','display','screen','touch','mouse','trackpad','keyboard','type','input','output','file','folder','dir','path','url','page','tab','window','dialog','popup','menu','button','avatar','pdf','zip','tar','exe','app','bin','dat','tmp','temp','src','build','dist','lib','test','docs','readme','license','todo','fixme','hack','wip','done','ship','ci','cd','dev','prod','stage','local','remote','origin','main','master','develop','feature','bugfix','hotfix','tag','commit','rebase','cherry','pick','stash','reset','revert','amend','squash','draft','pr','mr','issue','epic','story','task','ticket','sprint','backlog','roadmap','milestone','deadline','eta','asap','oc','tl','dr','ngmi','wagmi','w','l','looksmax','mewing','edging','gooning','fanum','tax','ohio','chad','gigachad','doomer','zoomer','boomer','millennial','genz','genx','okboomer','sksksk')
$conv = $convRaw | Where-Object { Test-Good $_ }
Write-Host "  conv: $($conv.Count)"

$wn = @()
if (Test-Path 'wordnet/wordnet_nouns_filtered.txt') { $wn += Get-Content 'wordnet/wordnet_nouns_filtered.txt' }
if (Test-Path 'wordnet/wordnet_verbs_filtered.txt') { $wn += Get-Content 'wordnet/wordnet_verbs_filtered.txt' }
if (Test-Path 'wordnet/wordnet_adjectives_filtered.txt') { $wn += Get-Content 'wordnet/wordnet_adjectives_filtered.txt' }
$wn = $wn | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } | Select-Object -Unique
Write-Host "  wordnet: $($wn.Count)"

$nor = @()
if (Test-Path 'norvig/norvig_clean.txt') {
  $nor = Get-Content 'norvig/norvig_clean.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { $_ }
  Write-Host "  norvig (pre-cleaned): $($nor.Count)"
} elseif (Test-Path 'norvig/norvig-words-filtered.txt') { 
  $nor = Get-Content 'norvig/norvig-words-filtered.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } | Select-Object -Unique 
  Write-Host "  norvig: $($nor.Count)"
}

$cands = ($kag + $foods + $conv + $wn + $nor) | Select-Object -Unique
Write-Host "Candidates after filters (pre-plural): $($cands.Count)"

if ($cands.Count -lt $required) {
  Write-Warning "Only $($cands.Count) candidates, but need $required. Will use what we have."
}

$toRemove = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($w in $cands) {
  if ($w.EndsWith('s') -and $w.Length -gt 3) {
    $r = $w.Substring(0, $w.Length-1)
    if ($cands -contains $r) { [void]$toRemove.Add($w) }
  }
  if ($w.EndsWith('es') -and $w.Length -gt 3) {
    $r = $w.Substring(0, $w.Length-2)
    if ($cands -contains $r) { [void]$toRemove.Add($w) }
  }
  if ($w.EndsWith('ies') -and $w.Length -gt 4) {
    $r = $w.Substring(0, $w.Length-3) + 'y'
    if ($cands -contains $r) { [void]$toRemove.Add($w) }
  }
  if ($w.EndsWith('ves') -and $w.Length -gt 4) {
    $r1 = $w.Substring(0, $w.Length-3) + 'f'
    $r2 = $w.Substring(0, $w.Length-3) + 'fe'
    if (($cands -contains $r1) -or ($cands -contains $r2)) { [void]$toRemove.Add($w) }
  }
}

$irreg = @{ 'men'='man'; 'women'='woman'; 'children'='child'; 'mice'='mouse'; 'lice'='louse'; 'geese'='goose'; 'teeth'='tooth'; 'feet'='foot'; 'people'='person'; 'oxen'='ox' }
foreach ($pl in $irreg.Keys) {
  $sg = $irreg[$pl]
  if (($cands -contains $sg) -and ($cands -contains $pl)) { [void]$toRemove.Add($pl) }
}

$final = $cands | Where-Object { -not $toRemove.Contains($_) } | Sort-Object | Select-Object -Unique
Write-Host "After singular preference + irregular removal: $($final.Count)"

# Priority: foods + conv first (in their internal alpha), then fill with rest (already sorted overall)
$priority = ($foods + $conv) | Sort-Object -Unique
$rest = $final | Where-Object { $priority -notcontains $_ }

$list = @()
$list += $priority
$need = $required - $list.Count
if ($need -gt 0) {
  $list += ($rest | Select-Object -First $need)
}
$list = $list | Select-Object -First $required

# Final plural safety pass on the selected list
$toRemove2 = New-Object 'System.Collections.Generic.HashSet[string]'
$lset = [System.Collections.Generic.HashSet[string]]::new([string[]]$list)
foreach ($w in $list) {
  if ($w.EndsWith('s') -and $w.Length -gt 3) { $r = $w.Substring(0,$w.Length-1); if ($lset.Contains($r)) { [void]$toRemove2.Add($w) } }
  if ($w.EndsWith('es') -and $w.Length -gt 3) { $r = $w.Substring(0,$w.Length-2); if ($lset.Contains($r)) { [void]$toRemove2.Add($w) } }
  if ($w.EndsWith('ies') -and $w.Length -gt 4) { $r = $w.Substring(0,$w.Length-3)+'y'; if ($lset.Contains($r)) { [void]$toRemove2.Add($w) } }
  if ($w.EndsWith('ves') -and $w.Length -gt 4) { 
    $r1 = $w.Substring(0,$w.Length-3)+'f'; $r2 = $w.Substring(0,$w.Length-3)+'fe'; 
    if ($lset.Contains($r1) -or $lset.Contains($r2)) { [void]$toRemove2.Add($w) } 
  }
}
foreach ($pl in $irreg.Keys) {
  $sg = $irreg[$pl]
  if ($lset.Contains($sg) -and $lset.Contains($pl)) { [void]$toRemove2.Add($pl) }
}
$list = $list | Where-Object { -not $toRemove2.Contains($_) } | Select-Object -First $required

Write-Host "Final selected count: $($list.Count)"

# Write outputs
$list | Set-Content 'curated-exact-64434.txt' -Encoding utf8
$list | Set-Content 'curated-by-chris-words.txt' -Encoding utf8

Write-Host "Written curated-exact-64434.txt and curated-by-chris-words.txt"

# Validation
Write-Host "=== First 20 (should start with foods/conv) ==="
$list | Select-Object -First 20

Write-Host "=== Last 5 ==="
$list | Select-Object -Last 5

Write-Host "=== Checking for any remaining s/p pairs ==="
$pairs = @()
$fset = [System.Collections.Generic.HashSet[string]]::new([string[]]$list)
foreach ($w in $list) {
  if ($w -match '^(.*)s$' -and $w.Length -gt 3) { $b=$matches[1]; if ($fset.Contains($b)) { $pairs += "$b/$w" } }
  if ($w -match '^(.*)es$' -and $w.Length -gt 3) { $b=$matches[1]; if ($fset.Contains($b)) { $pairs += "$b/$w" } }
  if ($w -match '^(.*)ies$' -and $w.Length -gt 4) { $b=$matches[1]+'y'; if ($fset.Contains($b)) { $pairs += "$b/$w" } }
  if ($w -match '^(.*)ves$' -and $w.Length -gt 4) { $b1=$w.Substring(0,$w.Length-3)+'f'; $b2=$w.Substring(0,$w.Length-3)+'fe'; if ($fset.Contains($b1) -or $fset.Contains($b2)) { $pairs += "$w" } }
}
foreach ($pl in $irreg.Keys) { $sg=$irreg[$pl]; if ($fset.Contains($sg) -and $fset.Contains($pl)) { $pairs += "$sg/$pl" } }
$pairs = $pairs | Select-Object -Unique
Write-Host "Plural/singular pairs found: $($pairs.Count)"
if ($pairs.Count -gt 0) { $pairs | Select-Object -First 10 } else { "Good: zero pairs" }

Write-Host "=== Sample priority words present ==="
@('adobo','aioli','wifi','meme','vibe','rizz','react','node') | Where-Object { $list -contains $_ } | ForEach-Object { $_ }

Write-Host "Done. Required=$required  Got=$($list.Count)"
