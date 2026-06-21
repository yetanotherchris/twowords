param(
  [string]$OutFile = "curated-v2.txt"
)

$ErrorActionPreference = "Stop"
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $base) { $base = "C:\Users\chris\Documents\GitHub\twowords\data\words" }
Set-Location $base

$stops = @('the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','day','get','has','him','his','how','man','new','now','old','see','two','way','who','boy','end','did','its','let','put','say','she','too','use','dad','mom','off','own','may','try','ask','big','per','act','set','yet','far','few','that','with','this','from','which','have','were','they','will','their','been','other','there','would','more','such','when','any','these','time','than','some','what','about','state','only','into','also','them','said','under','first','made','should','after','shall','your','most','could','then','over','each','year','work','where','years','between','those','same','many','through','upon','must','well','very','general','before','used','because','being','part','like','united','people','during','public','section','number','even','make','court','case','system','much','three','both','water','law','life','company','service','good','without','order','great','american','while','however','york','long','high','national','right','does','city','just','here','world','another','data','business','given','know','program','little','since','present','every','house','men','report','less','back','place','total','large','take','down','small','county','second','control','might','research','office','last','point','form','board','still','children','interest','federal','study','area','action','value','fact','line','found','power','states','within','school','against')

$cities = @{}
Get-Content "cities/uk_cities.txt" -ErrorAction SilentlyContinue | ForEach-Object {
  $t = $_.ToLower().Trim()
  if ($t) { $cities[$t] = $true }
}

$profs = @{}
Get-Content "profanity.txt" -ErrorAction SilentlyContinue | ForEach-Object {
  $t = $_.ToLower().Trim()
  if ($t -and $t.Length -ge 3 -and $t.Length -le 8) { $profs[$t] = $true }
}

function Test-Word([string]$w) {
  if (-not $w) { return $false }
  if ($w.Length -lt 3 -or $w.Length -gt 8) { return $false }
  if ($w -notmatch '^[a-z]+$') { return $false }
  if ($stops -contains $w) { return $false }
  if ($cities.ContainsKey($w)) { return $false }
  if ($profs.ContainsKey($w)) { return $false }
  return $true
}

function FilterList($path) {
  if (-not (Test-Path $path)) { return @() }
  Get-Content $path | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Word $_ }
}

# Foods (high priority)
$foods = FilterList "claude/food_dishes_final.txt" | Sort-Object -Unique

# Conversational / tech / modern (high priority)
$convRaw = @(
  'wifi','bluetooth','yapping','yap','meme','vibe','vibes','ghost','flex','troll','spam','ping','zoom','tweet','post','like','share','stream','chat','app','bug','crash','sync','cache','cloud','login','logout','update','swipe','scroll','tap','click','drag','drop','snap','selfie','story','reel','clip','filter','hashtag','emoji','gif','mood','cringe','sus','cap','bet','slay','lit','fire','dope','sick','yeet','rizz','skibidi','sigma','gyatt','delulu','bruh','drip','glow','hype','fomo','jomo','stan','shade','salty','savage','roast','burn','clapback','ratio','mid','bussin','cheugy','main','character','npc','alpha','beta','omega','goat','based','cope','seethe','lfg','dub','sheesh','fr','frfr','ong','pog','poggers','kek','kekw','lul','lmao','lmfao','rofl','af','asf','iykyk','fyi','tldr','imo','imho','idk','idc','smh','facepalm','wtf','wth','brb','afk','irl','fwiw','nsfw','sfw','ama','eli5','op','yolo','tiktok','insta','snapchat','reddit','discord','slack','teams','meet','skype','facetime','airdrop','airplay','hotspot','vpn','dns','ip','mac','gui','cli','api','sdk','ide','fix','patch','release','deploy','commit','push','pull','merge','branch','fork','clone','repo','git','npm','yarn','pip','cargo','docker','pod','helm','aws','gcp','azure','lambda','s3','cdn','ssl','tls','http','https','tcp','udp','ssh','ftp','jwt','oauth','sql','nosql','db','orm','react','vue','svelte','angular','astro','next','nuxt','vite','webpack','babel','ts','js','jsx','tsx','css','scss','sass','html','xml','json','yaml','yml','toml','md','csv','log','kafka','rabbit','redis','spark','flink','node','python','rust','java','kotlin','swift','go','ruby','php','shell','bash','zsh','fish','make','cmake','gradle','maven','nginx','haproxy','fastapi','flask','django','rails','spring','express','laravel','electron','flutter','ios','android','linux','macos','windows','unix','async','await','promise','thread','lock','queue','stack','heap','array','list','map','set','hash','tree','graph','vector','matrix','token','embed','prompt','agent','tool','chunk','index','faiss','duckdb','pandas','numpy','torch','jax','keras','llm','gpt','bert','diffusion','stable','genai','rag','ml','ai','web','net','site','link','feed','live','text','dm','tag','heart','save','view','play','pause','stop','skip','search','find','open','close','edit','delete','add','hot','cold','fast','slow','good','bad','nice','cool','fun','sad','happy','mad','tired','bored','busy','free','easy','hard','simple','clean','fresh','sweet','sour','spicy','loud','quiet','bright','dark','light','heavy','soft','wet','dry','warm','young','rich','poor','high','low','long','short','wide','deep','full','empty','true','false','yes','no','ok','fine','great','best','worst','first','last','next','top','bottom','left','right','center','front','back','edge','line','point','icon','image','photo','pic','video','audio','sound','music','song','beat','voice','talk','speak','say','tell','ask','answer','question','reply','comment','status','broadcast','podcast','radio','tv','netflix','youtube','messenger','webrtc','p2p','mesh','server','client','host','backup','restore','upgrade','install','uninstall','download','upload','cookie','session','signup','signin','auth','secret','password','pass','pin','encrypt','decrypt','hash','sign','verify','cert','proxy','firewall','router','switch','modem','display','screen','touch','mouse','trackpad','keyboard','type','input','output','file','folder','dir','path','url','page','tab','window','dialog','popup','menu','button','avatar','pdf','zip','tar','exe','app','bin','dat','tmp','temp','src','build','dist','lib','test','docs','readme','license','todo','fixme','hack','wip','done','ship','ci','cd','dev','prod','stage','local','remote','origin','main','master','develop','feature','bugfix','hotfix','tag','commit','rebase','cherry','pick','stash','reset','revert','amend','squash','draft','pr','mr','issue','epic','story','task','ticket','sprint','backlog','roadmap','milestone','deadline','eta','asap','oc','tl','dr','ngmi','wagmi','w','l','looksmax','mewing','edging','gooning','fanum','tax','ohio','chad','gigachad','doomer','zoomer','boomer','millennial','genz','genx','okboomer','sksksk'
)
$conv = $convRaw | Where-Object { Test-Word $_ } | Sort-Object -Unique

# Common sources
$kag = FilterList "kaggle/common_clean.txt"
$wnN = FilterList "wordnet/wordnet_nouns_filtered.txt"
$wnV = FilterList "wordnet/wordnet_verbs_filtered.txt"
$wnA = FilterList "wordnet/wordnet_adjectives_filtered.txt"
$wn = ($wnN + $wnV + $wnA) | Select-Object -Unique
$clc = FilterList "claude/common_words.txt"

$rest = ($kag + $wn + $clc) | Select-Object -Unique | Where-Object { $conv -notcontains $_ -and $foods -notcontains $_ } | Sort-Object

$final = @()
$final += ($foods | Sort-Object)
$final += ($conv | Sort-Object)
$final += $rest
$final = $final | Select-Object -Unique

Write-Output "Final word count: $($final.Count)"
$final | Set-Content -Encoding utf8 $OutFile

# Quick validation
$leaksCity = $final | Where-Object { $cities.ContainsKey($_) }
$leaksProf = $final | Where-Object { $profs.ContainsKey($_) }
Write-Output "City leaks: $(if ($leaksCity) { $leaksCity.Count } else { 0 })"
Write-Output "Prof leaks: $(if ($leaksProf) { $leaksProf.Count } else { 0 })"

Write-Output "Top 25:"
$final | Select-Object -First 25
Write-Output "--- Conv section sample ---"
$skip = $foods.Count
$final | Select-Object -Skip $skip -First 15
Write-Output "--- Random 10 ---"
$final | Get-Random -Count 10