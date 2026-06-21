param()
$ErrorActionPreference = 'Stop'
$base = 'C:\Users\chris\Documents\GitHub\twowords\data\words'
Set-Location $base

$required = 20288

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

$acroList = @('aaa','abc','api','aws','cdn','cli','cpu','css','dns','faq','ftp','gpu','gui','html','http','https','ide','ios','ip','iso','jpg','json','jwt','lcd','led','mac','md5','mp3','mp4','npm','pdf','png','ram','rom','rss','sdk','sql','ssh','ssl','svg','tcp','udp','url','usb','utf','vpn','xml','yaml','yml','gif','wav','mov','avi','exe','zip','tar','rar','deb','rpm','apk','ipa','bin','dat','tmp','log','src','lib','dev','prod','test','ci','cd','pr','mr','ui','ux','ai','ml','llm','gpt','bert','rag','db','orm','mvc','spa','pwa','wasm','webgl','sftp','saml','oidc','csrf','xss','nosql','rtc','p2p','www','csv','md','aps','aar','aas','aba','abb','acc','adh','aer','aet','afr','aft','aga','age','agi','aha','ahi','ahs','aid','ail','aim','air','ais','ait','ala','alb','ale','all','alp','alt','ama','ami','amp','amu','ana','and','ani','ant','any','ape','apo','app','apt','arc','are','arf','ark','arm','ars','art','ash','ask','asp','ass','ate','att','auk','ava','ave','avo','awa','awe','awl','awn','axe','aye','ays','azo','baa','bad','bae','bag','bah','bal','bam','ban','bar','bas','bat','bay','bed','bee','beg','bel','ben','bes','bet','bey','bib','bid','big','bin','bio','bis','bit','biz','boa','bob','bod','bog','boo','bop','bos','bot','bow','box','boy','bra','bro','brr','bub','bud','bug','bum','bun','bur','bus','but','buy','bye','bys','cab','cad','cam','can','cap','car','cat','caw','cay','cee','cel','cep','chi','cig','cis','cob','cod','cog','col','con','coo','cop','cor','cos','cot','cow','cox','coy','coz','cru','cry','cub','cud','cue','cum','cup','cur','cut','cwm','dab','dad','dag','dah','dak','dal','dam','dan','dap','daw','day','deb','dee','def','del','den','dev','dew','dex','dey','dib','did','die','dif','dig','dim','din','dip','dis','dit','doc','doe','dog','dol','dom','don','dor','dos','dot','dow','dry','dub','dud','due','dug','duh','dui','dun','duo','dup','dye','ear','eat','eau','ebb','ecu','edh','eds','eek','eel','eff','efs','eft','egg','ego','eke','eld','elf','elk','ell','elm','els','eme','ems','emu','end','eng','ens','eon','era','ere','erg','ern','err','ers','ess','eta','eth','eve','ewe','eye','fab','fad','fag','fan','far','fas','fat','fay','fed','fee','feh','fem','fen','fer','fes','fet','feu','few','fey','fez','fib','fid','fie','fig','fil','fin','fir','fit','fiz','flu','fly','fob','foe','fog','foh','fon','foo','fop','for','fou','fox','foy','fro','fry','fub','fud','fug','fun','fur','gab','gad','gae','gag','gal','gam','gan','gap','gar','gas','gat','gay','ged','gee','gel','gem','gen','get','gey','ghi','gib','gid','gie','gig','gin','gip','git','gnu','goa','gob','god','goo','gor','gos','got','gox','goy','gul','gum','gun','gut','guv','guy','gym','gyp','had','hae','hag','hah','haj','ham','hao','hap','has','hat','haw','hay','heh','hem','hen','hep','her','hes','het','hew','hex','hey','hic','hid','hie','him','hin','hip','his','hit','hmm','hob','hoc','hod','hoe','hog','hon','hop','hot','how','hoy','hub','hue','hug','huh','hum','hun','hup','hyp','ice','ich','ick','icy','ids','iff','ifs','igg','ilk','ill','imp','ink','inn','ins','ion','ire','irk','ism','its','ivy','jab','jag','jam','jar','jaw','jay','jee','jet','jeu','jew','jib','jig','jin','job','joe','jog','jot','jow','joy','jua','jug','jun','jus','jut','kab','kae','kaf','kas','kat','kay','kea','kef','keg','ken','kep','kex','key','khi','kid','kif','kin','kip','kir','kis','kit','koa','kob','koi','kop','kor','kos','kue','kye','lab','lac','lad','lag','lam','lap','lar','las','lat','lav','law','lax','lay','lea','led','lee','leg','lei','lek','les','let','leu','lev','lex','ley','lib','lid','lie','lin','lip','lis','lit','lob','log','loo','lop','lot','low','lox','lug','lum','luv','lux','lye','mac','mad','mae','mag','man','map','mar','mas','mat','maw','max','may','med','meg','mel','mem','men','met','mew','mho','mib','mic','mid','mig','mil','mim','mir','mis','mix','moa','mob','moc','mod','mog','mol','mom','mon','moo','mop','mor','mos','mot','mow','mud','mug','mum','mun','mus','mut','myc','nab','nae','nag','nah','nam','nan','nap','naw','nay','neb','nee','neg','net','new','nil','nim','nip','nit','nix','nob','nod','nog','noh','nom','noo','nor','nos','not','now','nth','nub','nug','nun','nus','nut','oaf','oak','oar','oat','oba','obe','obi','oca','oda','odd','ode','ods','oes','off','oft','ohm','oho','ohs','oil','oka','oke','old','ole','oms','one','ono','ons','ooh','oot','ope','ops','opt','ora','orb','orc','ore','ors','ort','ose','oud','our','out','ova','owe','owl','own','oxo','oxy','pac','pad','pah','pal','pam','pan','pap','par','pas','pat','paw','pax','pay','pea','pec','ped','pee','peg','peh','pen','pep','per','pes','pet','pew','phi','pht','pia','pic','pie','pig','pin','pip','pis','pit','piu','pix','ply','poh','poi','pol','pom','poo','pop','pot','pow','pox','pro','pry','psi','pst','pub','pud','pug','pul','pun','pup','pur','pus','put','pya','pye','pyx','qat','qis','qua','rad','rag','rah','rai','raj','ram','ran','rap','ras','rat','raw','rax','ray','reb','rec','red','ree','ref','reg','rei','rem','rep','res','ret','rev','rex','rho','ria','rib','rid','rif','rig','rim','rin','rip','rob','roc','rod','roe','rom','roo','rot','row','rub','rue','rug','rum','run','rut','rya','rye','sab','sac','sad','sae','sag','sal','sap','sat','sau','saw','sax','say','sea','sec','see','seg','sei','sel','sen','ser','set','sew','sha','she','shh','shy','sib','sic','sim','sin','sip','sir','sis','sit','ska','ski','sky','sly','sob','soc','sod','sol','som','son','sop','sos','sot','sou','sow','sox','soy','spa','spy','sri','sty','sub','sue','suk','sun','sup','suq','syn','tab','tad','tae','tag','taj','tam','tan','tao','tap','tar','tas','tat','tau','tav','taw','tea','ted','tee','teg','tel','ten','tet','tew','the','tho','thy','tic','tie','til','tin','tip','tis','tit','tod','toe','tog','tom','ton','too','top','tor','tot','tow','toy','try','tsk','tub','tug','tui','tun','tup','two','tye','udo','ugh','uke','ulu','umm','ump','uns','upo','ups','urb','urd','urn','urp','use','uta','ute','uts','vac','van','var','vas','vat','vau','vav','vaw','vee','veg','vet','vex','via','vid','vie','vig','vim','vis','voe','vow','vox','vug','vum','wab','wad','wae','wag','wan','wap','war','was','wat','waw','wax','way','web','wed','wee','wen','wet','wha','who','why','wis','wit','wiz','woe','wok','won','woo','wos','wot','wow','wry','wud','wye','wyn','xis','yag','yah','yak','yam','yap','yar','yas','yaw','yay','yea','yeh','yen','yep','yes','yet','yew','yid','yin','yip','yob','yod','yok','yom','yon','you','yow','yuk','yum','yup','zag','zap','zas','zax','zed','zee','zek','zep','zig','zin','zip','zit','zoa','zoo','zuz','zzz')
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

$kag = @()
if (Test-Path 'kaggle/common_clean.txt') { $kag = Get-Content 'kaggle/common_clean.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } }

$foods = @()
if (Test-Path 'claude/food_dishes_final.txt') { $foods = Get-Content 'claude/food_dishes_final.txt' | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ } }

$convRaw = @('wifi','bluetooth','yapping','yap','meme','vibe','vibes','ghost','flex','troll','spam','ping','zoom','tweet','post','like','share','stream','chat','app','bug','crash','sync','cache','cloud','login','logout','update','swipe','scroll','tap','click','drag','drop','snap','selfie','story','reel','clip','filter','hashtag','emoji','gif','mood','cringe','sus','cap','bet','slay','lit','fire','dope','sick','yeet','rizz','skibidi','sigma','gyatt','delulu','bruh','drip','glow','hype','fomo','jomo','stan','shade','salty','savage','roast','burn','clapback','ratio','mid','bussin','cheugy','main','character','npc','alpha','beta','omega','goat','based','cope','seethe','lfg','dub','sheesh','fr','frfr','ong','pog','poggers','kek','kekw','lul','lmao','lmfao','rofl','af','asf','iykyk','fyi','tldr','imo','imho','idk','idc','smh','facepalm','wtf','wth','brb','afk','irl','fwiw','nsfw','sfw','ama','eli5','op','yolo','tiktok','insta','snapchat','reddit','discord','slack','teams','meet','skype','facetime','airdrop','airplay','hotspot','vpn','dns','ip','mac','gui','cli','api','sdk','ide','fix','patch','release','deploy','commit','push','pull','merge','branch','fork','clone','repo','git','npm','yarn','pip','cargo','docker','pod','helm','aws','gcp','azure','lambda','s3','cdn','ssl','tls','http','https','tcp','udp','ssh','ftp','jwt','oauth','sql','nosql','db','orm','react','vue','svelte','angular','astro','next','nuxt','vite','webpack','babel','ts','js','jsx','tsx','css','scss','sass','html','xml','json','yaml','yml','toml','md','csv','log','kafka','rabbit','redis','spark','flink','node','python','rust','java','kotlin','swift','go','ruby','php','shell','bash','zsh','fish','make','cmake','gradle','maven','nginx','haproxy','fastapi','flask','django','rails','spring','express','laravel','electron','flutter','ios','android','linux','macos','windows','unix','async','await','promise','thread','lock','queue','stack','heap','array','list','map','set','hash','tree','graph','vector','matrix','token','embed','prompt','agent','tool','chunk','index','faiss','duckdb','pandas','numpy','torch','jax','keras','llm','gpt','bert','diffusion','stable','genai','rag','ml','ai','web','net','site','link','feed','live','text','dm','tag','heart','save','view','play','pause','stop','skip','search','find','open','close','edit','delete','add','hot','cold','fast','slow','good','bad','nice','cool','fun','sad','happy','mad','tired','bored','busy','free','easy','hard','simple','clean','fresh','sweet','sour','spicy','loud','quiet','bright','dark','light','heavy','soft','wet','dry','warm','young','rich','poor','high','low','long','short','wide','deep','full','empty','true','false','yes','no','ok','fine','great','best','worst','first','last','next','top','bottom','left','right','center','front','back','edge','line','point','icon','image','photo','pic','video','audio','sound','music','song','beat','voice','talk','speak','say','tell','ask','answer','question','reply','comment','status','broadcast','podcast','radio','tv','netflix','youtube','messenger','webrtc','p2p','mesh','server','client','host','backup','restore','upgrade','install','uninstall','download','upload','cookie','session','signup','signin','auth','secret','password','pass','pin','encrypt','decrypt','hash','sign','verify','cert','proxy','firewall','router','switch','modem','display','screen','touch','mouse','trackpad','keyboard','type','input','output','file','folder','dir','path','url','page','tab','window','dialog','popup','menu','button','avatar','pdf','zip','tar','exe','app','bin','dat','tmp','temp','src','build','dist','lib','test','docs','readme','license','todo','fixme','hack','wip','done','ship','ci','cd','dev','prod','stage','local','remote','origin','main','master','develop','feature','bugfix','hotfix','tag','commit','rebase','cherry','pick','stash','reset','revert','amend','squash','draft','pr','mr','issue','epic','story','task','ticket','sprint','backlog','roadmap','milestone','deadline','eta','asap','oc','tl','dr','ngmi','wagmi','w','l','looksmax','mewing','edging','gooning','fanum','tax','ohio','chad','gigachad','doomer','zoomer','boomer','millennial','genz','genx','okboomer','sksksk')
$conv = $convRaw | Where-Object { Test-Good $_ }

$wn = @()
if (Test-Path 'wordnet/wordnet_nouns_filtered.txt') { $wn += Get-Content 'wordnet/wordnet_nouns_filtered.txt' }
if (Test-Path 'wordnet/wordnet_verbs_filtered.txt') { $wn += Get-Content 'wordnet/wordnet_verbs_filtered.txt' }
if (Test-Path 'wordnet/wordnet_adjectives_filtered.txt') { $wn += Get-Content 'wordnet/wordnet_adjectives_filtered.txt' }
$wn = $wn | ForEach-Object { $_.ToLower().Trim() } | Where-Object { Test-Good $_ }

$cands = ($kag + $foods + $conv + $wn) | Select-Object -Unique
Write-Host "Candidates after filters (pre-plural): $($cands.Count)"

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
}

$final = $cands | Where-Object { -not $toRemove.Contains($_) } | Sort-Object | Select-Object -Unique
Write-Host "Final count after singular preference: $($final.Count)"

if ($final.Count -lt $required) {
  Write-Warning "Short of $required, keeping best we have."
}

$final | Set-Content 'curated-alpha-final.txt' -Encoding utf8

Write-Host '=== First 30 ==='
$final | Select-Object -First 30
Write-Host '=== Foods/conv sample ==='
$sample = @('adobo','aioli','baklava','chorizo','wifi','bluetooth','yapping','meme','vibe','rizz','skibidi','sigma','react','vue','node','python','rust','java','kotlin','swift','go','ruby','bash','zsh','fish','make','cmake','gradle','maven','nginx','fastapi','flask','django','rails','spring','express','laravel','electron','flutter','ios','android','linux','macos','windows','unix','async','await','promise','thread','lock','queue','stack','heap','array','list','map','set','hash','tree','graph','vector','matrix','token','embed','prompt','agent','tool','chunk','index','faiss','duckdb','pandas','numpy','torch','jax','keras','llm','gpt','bert','diffusion','stable','genai','rag','ml','ai')
$present = $sample | Where-Object { $final -contains $_ } | Select-Object -First 15
Write-Host ($present -join ' ')
Write-Host '=== Random 10 ==='
$final | Get-Random -Count 10
Write-Host '=== Plural check (no pairs) ==='
$checks = @('horse','horses','man','men','woman','women','child','children','mouse','mice','goose','geese','tooth','teeth','foot','feet','person','people')
foreach ($c in $checks) {
  $has = if ($final -contains $c) { 'YES' } else { 'no' }
  Write-Host "$c : $has"
}
Write-Host "Written curated-alpha-final.txt ($($final.Count) words)"