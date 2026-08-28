$ErrorActionPreference = 'Stop'

$siteRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$v1HtmlPath = Join-Path $siteRoot 'v1\index.html'
$v2HtmlPath = Join-Path $siteRoot 'v2\index.html'
$v1HeroPath = Join-Path $siteRoot 'v1\assets\japan-hero.png'
$v2HeroPath = Join-Path $siteRoot 'v2\assets\japan-hero.png'

function Assert-True([bool]$condition, [string]$message) {
  if (-not $condition) { throw "FAIL: $message" }
  Write-Host "PASS: $message"
}

Assert-True (Test-Path -LiteralPath $v1HtmlPath) 'v1 HTML exists'
Assert-True (Test-Path -LiteralPath $v2HtmlPath) 'v2 HTML exists'
Assert-True (Test-Path -LiteralPath $v1HeroPath) 'v1 hero asset exists'
Assert-True (Test-Path -LiteralPath $v2HeroPath) 'v2 hero asset exists'

$v1HtmlHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $v1HtmlPath).Hash
$v1HeroHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $v1HeroPath).Hash
Assert-True ($v1HtmlHash -eq 'EE8CA7B6280BC8C8FE548C0D5BE3E158B83F180883F5C1E4070ED28B66DA2301') 'v1 HTML is frozen byte-for-byte'
Assert-True ($v1HeroHash -eq '04DED1578758432B3A2823F341E8BC94B6E5F1154CB3D1D74E165FEBF6316AE3') 'v1 hero is frozen byte-for-byte'

$v2 = Get-Content -Raw -LiteralPath $v2HtmlPath
$motionContracts = @(
  'class="scroll-progress"',
  'class="cursor-orb"',
  'class="ambient-lines"',
  'data-parallax',
  'data-magnetic',
  'data-tilt',
  'initPointerGlow',
  'initParallax',
  'initMagnetic',
  'initKineticType',
  'initCardTilt'
)
foreach ($contract in $motionContracts) {
  Assert-True ($v2.Contains($contract)) "v2 includes motion contract: $contract"
}

Assert-True ($v2.Contains('@media (prefers-reduced-motion: reduce)')) 'v2 keeps reduced-motion accessibility'
Assert-True (-not ($v2 -match '(?i)не бронь|без гонк|это предложение|рабочая версия')) 'v2 does not restore discarded draft phrasing'

# Performance contracts for the optimized motion edition.
Assert-True (-not $v2.Contains('mix-blend-mode: screen')) 'v2 avoids expensive full-screen blend compositing'
Assert-True (-not $v2.Contains('requestAnimationFrame(tick)')) 'pointer glow does not run a perpetual animation loop'
Assert-True (-not ($v2 -match '@keyframes breathe\s*\{[^}]*filter:')) 'hero does not animate GPU-expensive filters'
$scrollListenerCount = ([regex]::Matches($v2, 'addEventListener\("scroll"')).Count
Assert-True ($scrollListenerCount -eq 1) 'v2 uses one scheduled scroll motion pipeline'
Assert-True ($v2.Contains('function initMotionEngine')) 'v2 centralizes scroll and pointer animation work'
Assert-True ($v2.Contains('content-visibility: auto')) 'off-screen sections defer rendering work'

# Visual-energy contracts: transform-only effects that keep the premium direction.
Assert-True ($v2.Contains('class="kiss-line"')) 'v2 includes the lacquer-red gesture accent'
Assert-True ($v2.Contains('class="silk-veil"')) 'v2 includes the silk reveal transition'
Assert-True ($v2.Contains('class="card-glint"')) 'v2 itinerary cards include a restrained moving glint'

# Day-sheet interaction contracts.
Assert-True ($v2.Contains('<dialog class="day-sheet" id="daySheet"')) 'v2 provides a native accessible day sheet'
Assert-True ($v2.Contains('aria-labelledby="daySheetTitle"')) 'day sheet has an accessible title relationship'
Assert-True ($v2.Contains('role="button" tabindex="0"')) 'itinerary cards are keyboard-focusable controls'
Assert-True ($v2.Contains('data-day="${d[0]}"')) 'each generated card carries its day identifier'
Assert-True ($v2.Contains('const dayDetails =')) 'v2 includes structured details for all days'
Assert-True (([regex]::Matches($v2, 'dayDetails\["(0[1-9]|10)"\]')).Count -ge 1) 'day-sheet rendering reads structured details by day'
Assert-True ($v2.Contains('function openDaySheet')) 'v2 implements opening a selected day'
Assert-True ($v2.Contains('function closeDaySheet')) 'v2 implements explicit sheet closing'
Assert-True ($v2.Contains('loading="lazy"')) 'day-sheet images load lazily'
$dayImageRoot = Join-Path $siteRoot 'v2\assets\days'
Assert-True (Test-Path -LiteralPath $dayImageRoot) 'local day-image directory exists'
$dayImageCount = @(Get-ChildItem -LiteralPath $dayImageRoot -File -ErrorAction SilentlyContinue).Count
Assert-True ($dayImageCount -ge 8) 'v2 keeps a compact local set of at least eight place images'

# Proportion and hierarchy regression contracts from visual review.
Assert-True (-not $v2.Contains('class="kinetic-band"')) 'route transition no longer repeats the cities in a red banner'
Assert-True (-not $v2.Contains('class="route-divider"')) 'generic route divider is removed'
Assert-True ($v2.Contains('class="editorial-interlude"')) 'route transitions through a fashion editorial interlude'
Assert-True ($v2.Contains('class="editorial-ten"')) 'fashion interlude uses the oversized ten-days motif'
Assert-True ($v2.Contains('class="edition-label"')) 'fashion interlude carries a restrained issue label'
Assert-True ($v2.Contains('height:min(78svh,780px)')) 'desktop day sheet has a compact proportional height cap'
Assert-True ($v2.Contains('width:min(1180px,calc(100% - 64px))')) 'desktop day sheet has balanced side margins'
Assert-True ($v2.Contains('.day-gallery { height:260px; min-height:0;')) 'desktop gallery has a stable compact height'
Assert-True ($v2.Contains('@media (max-width: 850px)')) 'day sheet retains its mobile bottom-sheet breakpoint'
Assert-True ($v2.Contains('.route-line {') -and $v2.Contains('overflow: visible;')) 'city route allows hover halos outside the row box'
Assert-True ($v2.Contains('.stop-dot { position: relative; z-index: 3;')) 'city dots render above route lines'
Assert-True (-not $v2.Contains('class="day-credits"')) 'visible photo-credit paragraph is removed from the day sheet'
Assert-True (-not $v2.Contains('Кадры уменьшены и адаптированы')) 'day sheet no longer prints technical image notes'
Assert-True ($v2.Contains('class="photo-info"')) 'photo provenance remains available through a compact image control'
Assert-True ($v2.Contains('assets/days/evening-kyoto.jpg')) 'Kyoto arrival uses a real evening Kyoto image'
$eveningKyotoPath = Join-Path $siteRoot 'v2\assets\days\evening-kyoto.jpg'
Assert-True (Test-Path -LiteralPath $eveningKyotoPath) 'evening Kyoto image is stored locally'

# The attraction block sells four reasons for the trip, not itinerary timing.
$momentsMatch = [regex]::Match($v2, '<section class="moments"[\s\S]*?</section>')
Assert-True ($momentsMatch.Success) 'attraction section is present'
$moments = $momentsMatch.Value
$momentHeadings = @(
  'Токио — культура столицы',
  'Фудзи — главный пейзаж',
  'Киото — живая традиция',
  'Осака — энергия и вкус'
)
foreach ($heading in $momentHeadings) {
  Assert-True ($moments.Contains("<h3>$heading</h3>")) "attraction block uses destination-led heading: $heading"
}
Assert-True (-not ($moments -match '\d+(?:[,.]\d+)?\s*(?:–|-)?\s*\d*(?:[,.]\d+)?\s*час')) 'attraction block contains no walking-duration copy'
Assert-True ($moments.Contains('THE JOJO WORLD и IGGY CAFE')) 'Tokyo detail line keeps the personal JoJo highlight'

# Osaka days need distinct imagery: Dotonbori belongs to the evening route,
# while the food-and-shopping day should show Kuromon Market.
$dayNineMatch = [regex]::Match($v2, '"09"\s*:\s*\{[^\r\n]*')
Assert-True ($dayNineMatch.Success) 'day 09 detail data is present'
Assert-True (-not $dayNineMatch.Value.Contains('assets/days/dotonbori.jpg')) 'day 09 does not duplicate the day 08 Dotonbori image'
Assert-True ($dayNineMatch.Value.Contains('assets/days/kuromon-market.jpg')) 'day 09 uses its own Kuromon Market image'
$kuromonMarketPath = Join-Path $siteRoot 'v2\assets\days\kuromon-market.jpg'
Assert-True (Test-Path -LiteralPath $kuromonMarketPath) 'Kuromon Market image is stored locally'
Write-Host 'ALL VERSION TESTS PASSED'
