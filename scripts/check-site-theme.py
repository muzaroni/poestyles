"""Check the site stylesheet against source HTML fixtures in headless Chrome."""
from pathlib import Path
import html
import json
import os
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
styles = json.loads((root / 'poe-trade-compact.stylus.json').read_text(encoding='utf-8'))
assert isinstance(styles, list) and len(styles) == 1
css = styles[0]['sections'][0]['code']
fixtures = root / '.source-better-trading/test/integrations/poe-trade/fixtures'
filters = (fixtures / 'property-filters.html').read_text(encoding='utf-8')
item = (fixtures / 'poe2-headhunter.html').read_text(encoding='utf-8')
live_details = (root / 'tests/fixtures/listing-details.html').read_text(encoding='utf-8')
toolbar_html = (root / 'tests/fixtures/search-toolbar.html').read_text(encoding='utf-8')
account_html = (root / 'tests/fixtures/account-header.html').read_text(encoding='utf-8')
baseline = '''
body{background:#101010 linear-gradient(#101010,#030303);color:white}
.content{background-image:linear-gradient(#040404,#010101)}
.newItemContainer{position:absolute;left:44px;top:24px;height:96px;margin-left:44px;padding-left:10px}.iconContainer{position:absolute;left:12px;top:10px;height:96px;padding-left:8px}
.left>button.refresh{width:32px;height:26px;position:absolute;top:4px;left:4px}
.left>button.copy{position:absolute;bottom:4px;left:4px}
.left>button.searchBy{position:absolute;bottom:4px;left:40px}
.logo{height:180px}.logo img{height:160px;width:240px}
[data-test=section-header]{display:flex;align-items:center;min-height:26px;padding:2px 0}
[data-test=title-cell]{flex:1;background:black;border:1px solid #333;padding:2px 4px;line-height:20px}
.filter{height:26px}
.filter-body{display:flex;align-items:center;height:26px}
.filter-title{min-width:90px}
.multiselect{min-height:26px}
.multiselect__tags{border:1px solid #333;padding:2px}
.multiselect__option--selected{background:#633800}
.item-popup__header--unique{color:#af6025;background:#281810}
.item-mod--explicit{color:#88f}
.online{color:#2fa34f}.socket.red{background:#e34848}
.filter input.minmax{height:24px;padding:1px 4px;line-height:20px;box-sizing:border-box}
button.livesearch-btn.active{background:#075d29}
button.contact.sent{background:#214b24}
button.copy,button.searchBy{width:26px;height:26px;font-family:"Native Icons";background-image:linear-gradient(white,white);background-size:16px 16px;background-repeat:no-repeat}
.row.fixture-hover,.row.fixture-hover .middle,.row.fixture-hover .details{background-color:#555}
.details>.info{position:absolute;right:0;top:0}
.bt-equivalent-pricings{display:block}
.price{margin-right:6px}
.search-bar{display:flex;min-height:40px}
.search-left{width:60%;float:left;background:#000}.search-right{width:40%;display:flex;float:right;background:#000}
.controls{display:flex;min-height:42px;margin:8px 0}.controls-left,.controls-center,.controls-right{width:33.33%}
.controls button{padding:8px 14px;min-width:120px}
.controls-left .livesearch-btn{min-width:320px}
.search-bar .multiselect{position:relative;min-height:40px}
.search-bar .multiselect__tags{min-height:40px;box-sizing:border-box}
.search-bar .multiselect__select{position:absolute;right:0;top:0;width:20px}
[data-test=toolbar-navigation]{height:32px}
.resultset>.row{display:flex;position:relative}
.resultset>.row>.left{position:static;width:160px;flex:0 0 160px;padding:24px 20px 44px;box-sizing:border-box}
/* Compact-mode conflict cases reproduced from the observed arrangement. */
#trade .resultset .row .right .details{display:flex!important;flex-direction:row!important}
#trade .resultset .row .right .details>.price{width:38%!important;flex:0 0 38%!important}
#trade .resultset .row .right .details>.btns{width:60%!important}
#trade .resultset .row .right .details>.price>.bt-equivalent-pricings{display:block!important;flex-basis:100%!important}
#trade .resultset .row .right .details>.btns>.btn-group{width:100%!important;flex-basis:100%!important}
#trade{--colour-unmet:#e34848;--colour-currency:#aa9e82;--colour-value-default:#fff}
'''
markup = '<main class="content"><div class="wrapper"><div class="logo"><a href="#logo"><img alt="PoE" src="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22240%22 height=%22160%22%3E%3C/svg%3E"></a></div><div id="trade"><section class="search-panel"><div class="search-bar"><input placeholder="Search"></div><div class="filter-group"><div data-test="section-header"><button class="toggle-btn">Toggle</button><span data-test="title-cell">Filters</span></div><div data-test="collapse-wrapper" style="height:0;overflow:hidden"></div><div class="filter-group-body">' + filters + '</div></div><button class="search-btn">Search</button><button class="clear-btn" disabled>Clear</button><button class="livesearch-btn active">Live</button></section><div class="resultset"><div class="row" data-id="test"><div class="left"><span class="socket red">socket</span><button class="copy" title="Copy item"></button><button class="searchBy" title="Filter item"></button></div>' + item + '<div class="details"><span class="online">Online</span><div class="btns"><button class="btn btn-default" data-action="travel">Travel to Hideout</button><button class="btn btn-default" data-action="ignore">Ignore Player</button><button class="btn btn-default bt-pin-button" data-action="pin">Pin</button><button class="btn btn-default" style="display:none" data-action="hidden">Hidden</button><button class="contact sent">Sent</button></div></div></div></div></div></div></main><better-trading></better-trading><pre id="results">pending</pre>'
markup = markup.replace(
    '<div data-test="section-header"><button class="toggle-btn">Toggle</button><span data-test="title-cell">Filters</span></div>',
    '<div class="filter-group-header" data-test="section-header"><div class="filter"><span class="input-group-btn"><button class="toggle-btn off">Toggle</button></span><span class="filter-body"><span class="filter-title filter-title-clickable" data-test="title-cell">Filters</span></span></div></div>',
)
checks = r'''
const resultset = document.querySelector('.resultset');
const compact = document.createElement('div'); compact.className = 'results compact';
resultset.replaceWith(compact); compact.append(resultset);
const imageRow = document.createElement('div'); imageRow.className = 'row'; imageRow.dataset.id = 'image-test';
imageRow.style.cssText = 'width:640px;height:240px';
imageRow.innerHTML = '<div class="left"><button class="refresh" title="Refresh"></button><button class="copy" title="Copy Item"></button><button class="searchBy" title="Filter by Item Stats"></button><div class="newItemContainer itemRendered iW2 iH1"><div class="iconContainer"><div class="icon"><img width="48" height="48" alt="Item" src="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2248%22 height=%2248%22/%3E"></div><div class="verifiedStatus">Verified</div></div></div></div><div class="right">Item text</div>';
resultset.append(imageRow);
const nativeImageColumnWidth = imageRow.querySelector('.left').getBoundingClientRect().width;
const nativeImagePosition = getComputedStyle(imageRow.querySelector('.newItemContainer')).position;
const nativeImageDisplay = getComputedStyle(imageRow.querySelector('.left')).display;
const nativeTools = ['refresh','copy','searchBy'].map(name => {const b=imageRow.querySelector('button.'+name).getBoundingClientRect();const r=imageRow.getBoundingClientRect();return {left:b.left-r.left,top:b.top-r.top};});
const liveRow = document.createElement('div');
liveRow.className = 'row'; liveRow.dataset.id = 'live';
liveRow.style.cssText = 'width:640px;position:relative';
liveRow.innerHTML = '<div class="right">' + DETAILS_HTML + '</div>';
document.querySelector('.resultset').append(liveRow);
const toolbarHost = document.createElement('section');
toolbarHost.dataset.test = 'toolbar-host';
toolbarHost.innerHTML = '<nav data-test="toolbar-navigation">Search Listed Items | Exchange | Settings | About</nav>' + TOOLBAR_HTML;
document.querySelector('#trade').append(toolbarHost);
document.querySelector('#trade').style.width = '1900px';
const nativeToolbarHeight = toolbarHost.getBoundingClientRect().height;
const checks = [];
function check(label, pass) { checks.push({label, pass: Boolean(pass)}); }
const beforeHeight = document.querySelector('.filter-group').getBoundingClientRect().height;
const beforeLogoHeight = document.querySelector('.logo').getBoundingClientRect().height;
const beforeInputHeight = document.querySelector('.minmax').getBoundingClientRect().height;
const beforeBackground = getComputedStyle(document.body).backgroundImage;
const beforeWrapperBackground = getComputedStyle(document.querySelector('.content')).backgroundImage;
const beforeCopyImage = getComputedStyle(document.querySelector('button.copy')).backgroundImage;
const beforeFilterImage = getComputedStyle(document.querySelector('button.searchBy')).backgroundImage;
const beforeIconFont = getComputedStyle(document.querySelector('button.copy')).fontFamily;
const style = document.createElement('style'); style.textContent = CSS;
document.head.append(style);
const faces = await document.fonts.load('12px "PT JetBrains Mono"');
check('embedded font loads', faces.length > 0 && faces.every(face => face.status === 'loaded'));
const $ = selector => document.querySelector(selector);
const c = selector => getComputedStyle($(selector));
check('page black', getComputedStyle(document.body).backgroundColor === 'rgb(0, 0, 0)');
check('logo artwork hidden but header space retained', c('.logo').visibility === 'hidden' && document.querySelector('.logo').getBoundingClientRect().height === 64);
// Logo hidden on pinned layouts.
check('translucent main backing', c('#trade').backgroundColor === 'rgba(0, 0, 0, 0.76)');
check('filter groups do not stack opaque backgrounds', c('.filter-group').backgroundColor === 'rgba(0, 0, 0, 0)');
check('section box borders removed', c('.filter-group').borderLeftWidth === '0px' && c('.filter-group').borderTopWidth === '0px');
check('filter body stays transparent', c('.filter-group-body').backgroundColor === 'rgba(0, 0, 0, 0)');
check('filter columns reveal translucent trade backing', c('[data-test=toolbar-host] .search-left').backgroundColor === 'rgba(0, 0, 0, 0)' && c('[data-test=toolbar-host] .search-right').backgroundColor === 'rgba(0, 0, 0, 0)');
check('blue search action', c('.search-btn').backgroundColor === 'rgb(22, 48, 68)');
check('selected dropdown option distinct', c('.multiselect__option--selected').backgroundColor === 'rgb(50, 37, 25)');
check('disabled clear remains disabled', $('.clear-btn').disabled);
check('subtle blue-gray section header', c('[data-test=section-header]').backgroundColor === 'rgb(8, 14, 18)' && c('[data-test=section-header]').boxShadow.includes('rgb(24, 38, 46)'));
check('title cell lets full charcoal bar show through', c('[data-test=title-cell]').backgroundColor === 'rgba(0, 0, 0, 0)' && c('[data-test=title-cell]').borderTopWidth === '0px');
check('native input height preserved', $('.minmax').getBoundingClientRect().height === beforeInputHeight);
check('collapsed wrapper stays zero height', $('[data-test=collapse-wrapper]').getBoundingClientRect().height === 0);
check('section is no taller than native fixture', $('.filter-group').getBoundingClientRect().height <= beforeHeight);
check('native body artwork retained', getComputedStyle(document.body).backgroundImage === beforeBackground);
check('native wrapper artwork retained', c('.content').backgroundImage === beforeWrapperBackground);
check('result card stays transparent', c('.resultset > .row').backgroundColor === 'rgba(0, 0, 0, 0)');
check('native image column layout preserved', imageRow.querySelector('.left').getBoundingClientRect().width === nativeImageColumnWidth && getComputedStyle(imageRow.querySelector('.left')).display === nativeImageDisplay);
check('native image positioning preserved', getComputedStyle(imageRow.querySelector('.newItemContainer')).position === nativeImagePosition);
check('action icon coordinates unchanged', ['refresh','copy','searchBy'].every((name,i) => {const b=imageRow.querySelector('button.'+name).getBoundingClientRect();const r=imageRow.getBoundingClientRect();return Math.abs(b.left-r.left-nativeTools[i].left)<1 && Math.abs(b.top-r.top-nativeTools[i].top)<1;}));
check('native refresh stays at top', getComputedStyle(imageRow.querySelector('.refresh')).top === '4px' && getComputedStyle(imageRow.querySelector('.refresh')).left === '4px');
check('native copy and filter stay at bottom', getComputedStyle(imageRow.querySelector('.copy')).bottom === '4px' && getComputedStyle(imageRow.querySelector('.searchBy')).left === '40px');
check('item image size unchanged', imageRow.querySelector('img').getBoundingClientRect().width === 48 && imageRow.querySelector('img').getBoundingClientRect().height === 48);
check('image controls remain present', getComputedStyle(imageRow.querySelector('.copy')).display !== 'none' && getComputedStyle(imageRow.querySelector('.searchBy')).display !== 'none');
check('copy icon artwork preserved', c('button.copy').backgroundImage === beforeCopyImage && beforeCopyImage !== 'none');
check('filter icon artwork preserved', c('button.searchBy').backgroundImage === beforeFilterImage && beforeFilterImage !== 'none');
check('native icon font preserved', c('button.copy').fontFamily === beforeIconFont);
check('unique rarity color preserved', c('.item-popup__header--unique').color === 'rgb(175, 96, 37)');
check('modifier color preserved', c('.item-mod--explicit').color === 'rgb(136, 136, 255)');
check('corrupted warning preserved', c('[style*="colour-unmet"]').color === 'rgb(227, 72, 72)');
check('online indicator preserved', c('.online').color === 'rgb(47, 163, 79)');
check('socket color preserved', c('.socket.red').backgroundColor === 'rgb(227, 72, 72)');
check('live state preserved', c('.livesearch-btn').backgroundColor === 'rgb(7, 93, 41)');
check('contact state preserved', c('.contact').backgroundColor === 'rgb(33, 75, 36)');
check('listing default actions styled', c('[data-action=travel]').backgroundColor === 'rgba(8, 8, 8, 0.92)' && c('[data-action=ignore]').fontSize === '12px');
check('pin hidden as requested', c('[data-action=pin]').display === 'none');
check('native hidden action stays hidden', c('[data-action=hidden]').display === 'none');
const live = liveRow.querySelector('.details');
const priceBar = live.querySelector('.price');
const accountBar = live.querySelector('.btns');
const travel = live.querySelector('.direct-btn');
const ignore = live.querySelector('.ignore-btn');
const account = live.querySelector('.character-name');
check('live markup prices above account row', priceBar.getBoundingClientRect().bottom <= accountBar.getBoundingClientRect().top);
check('live markup asking fee conversion share one row', new Set([...priceBar.children].map(el => Math.round(el.getBoundingClientRect().top + el.getBoundingClientRect().height/2))).size === 1);
check('live markup account ignore travel order', account.getBoundingClientRect().left < ignore.getBoundingClientRect().left && ignore.getBoundingClientRect().left < travel.getBoundingClientRect().left);
check('live markup travel is right aligned', Math.abs(travel.getBoundingClientRect().right - accountBar.getBoundingClientRect().right) < 2);
check('expired Travel remains disabled', travel.disabled && travel.title === 'Item must be refreshed');
check('live markup Pin is hidden', getComputedStyle(live.querySelector('.bt-pin-button')).display === 'none');
liveRow.style.width = '320px';
check('live markup pricing and actions wrap without overflow', liveRow.scrollWidth <= liveRow.clientWidth + 1);
liveRow.style.width = '640px';
const toolbar = toolbarHost.querySelector('.search-panel');
const bar = toolbar.querySelector('.search-bar');
const actions = toolbar.querySelector('.controls');
const dockedField = bar.querySelector('.search-left > .search-select');
const leftFilters = document.createElement('section'); leftFilters.className = 'search-advanced-pane'; leftFilters.style.display='none'; leftFilters.append(document.querySelector('.filter-group').cloneNode(true));
const rightFilters = leftFilters.cloneNode(true);
bar.querySelector('.search-left').append(leftFilters); bar.querySelector('.search-right').append(rightFilters);
const middleY = el => { const r=el.getBoundingClientRect(); return (r.top+r.bottom)/2; };
check('wide toolbar merges fields and actions', Math.abs(middleY(dockedField)-middleY(actions)) < 1);
const toolbarLiveButton = actions.querySelector('.livesearch-btn');
const toolbarSearchLabel = actions.querySelector('.search-btn span');
const originalSearchLabel = toolbarSearchLabel.textContent;
const searchWidth = actions.querySelector('.search-btn').getBoundingClientRect().width;
toolbarSearchLabel.textContent = 'Live Search: Searching...';
actions.querySelector('.search-btn').disabled = true;
check('active live search keeps one toolbar row', Math.abs(middleY(dockedField)-middleY(actions)) < 1);
check('active tower icon is red', getComputedStyle(toolbarLiveButton, '::after').backgroundColor === 'rgb(224, 90, 84)');
check('active search shows short Live label', getComputedStyle(actions.querySelector('.search-btn'), '::after').content === '"Live..."' && actions.querySelector('.search-btn').getBoundingClientRect().width <= searchWidth + 10);
actions.querySelector('.search-btn').disabled = false;
toolbarSearchLabel.textContent = originalSearchLabel;
check('inactive live search keeps one toolbar row', Math.abs(middleY(dockedField)-middleY(actions)) < 1);
check('inactive search shows original label', getComputedStyle(actions.querySelector('.search-btn'), '::after').content === 'none' && getComputedStyle(toolbarLiveButton, '::after').backgroundColor === 'rgb(230, 173, 65)');
check('collapsed toolbar leaves no empty search-bar row', bar.getBoundingClientRect().height === 0);
const selectorsToActionsGap = actions.querySelector('.livesearch-btn').getBoundingClientRect().left - bar.querySelector('.search-right > .status-select:nth-child(3)').getBoundingClientRect().right;
check('status selectors extend toward actions (' + Math.round(selectorsToActionsGap) + 'px)', selectorsToActionsGap < 48);
check('compact actions show icons', ['.livesearch-btn', '.clear-btn', '.toggle-search-btn'].every(selector => getComputedStyle(actions.querySelector(selector), '::after').maskImage !== 'none'));
check('navigation remains below header', toolbarHost.querySelector('nav').getBoundingClientRect().top >= document.querySelector('.logo').getBoundingClientRect().bottom);
check('wide toolbar is shorter than native three rows', toolbarHost.getBoundingClientRect().height < nativeToolbarHeight);
check('advanced filters span below merged toolbar', toolbar.querySelector('[data-test=toolbar-advanced]').getBoundingClientRect().top >= Math.max(bar.getBoundingClientRect().bottom, actions.getBoundingClientRect().bottom));
check('all toolbar buttons remain visible', [...actions.querySelectorAll('button')].every(el => el.getBoundingClientRect().width > 0 && getComputedStyle(el).display !== 'none'));
const nativeHiddenToolbar = actions.cloneNode(true); nativeHiddenToolbar.style.display = 'none'; toolbar.append(nativeHiddenToolbar);
check('native hidden duplicate toolbar stays hidden', getComputedStyle(nativeHiddenToolbar).display === 'none'); nativeHiddenToolbar.remove();
const toggleChevron = actions.querySelector('.toggle-search-btn .chevron');
toggleChevron.classList.remove('collapsed');
leftFilters.style.display='block'; rightFilters.style.display='block';
const expandedControls = actions.cloneNode(true); leftFilters.append(expandedControls);
check('expanded copy of actions stays hidden', getComputedStyle(expandedControls).display === 'none');
check('filter wrappers remain in document flow', getComputedStyle(bar).position !== 'fixed' && getComputedStyle(leftFilters.parentElement).position !== 'fixed' && getComputedStyle(rightFilters.parentElement).position !== 'fixed');
check('filter columns keep usable width', leftFilters.parentElement.getBoundingClientRect().width > 500 && rightFilters.parentElement.getBoundingClientRect().width > 500);
check('opening filters keeps native panel layout', getComputedStyle(toolbar).display !== 'grid');
check('open filters keep combined pinned toolbar', Math.abs(middleY(dockedField)-middleY(actions)) < 1 && getComputedStyle(actions).position === 'fixed');
check('open filters keep advanced pane below actions', toolbar.querySelector('[data-test=toolbar-advanced]').getBoundingClientRect().top >= actions.getBoundingClientRect().bottom);
toggleChevron.classList.add('collapsed');
leftFilters.style.display='none'; rightFilters.style.display='none';
check('hiding filters restores compact row', Math.abs(middleY(dockedField)-middleY(actions)) < 1);
check('toolbar dropdowns stay closed', [...bar.querySelectorAll('.multiselect__content-wrapper')].every(el => getComputedStyle(el).display === 'none'));
check('toolbar reserves header space', Math.abs(dockedField.getBoundingClientRect().left-Math.min(400, Math.max(320, innerWidth*.18))) < 1);
check('search input fits inset field', dockedField.querySelector('input').getBoundingClientRect().right <= dockedField.getBoundingClientRect().right);
check('toolbar right edge stays at trade boundary', Math.abs(actions.getBoundingClientRect().right-document.querySelector('#trade').getBoundingClientRect().right)<1);
check('wide toolbar has no horizontal overflow', toolbar.scrollWidth <= toolbar.clientWidth+1);
document.querySelector('#trade').style.width = '1400px';
check('merged toolbar fits breakpoint width', toolbar.scrollWidth <= toolbar.clientWidth+1 && Math.abs(middleY(dockedField)-middleY(actions)) < 1);
document.querySelector('#trade').style.width = '1000px';
check('responsive inset survives trade area resize', Math.abs(dockedField.getBoundingClientRect().left-Math.min(400, Math.max(320, innerWidth * .18)))<1);
document.querySelector('#trade').style.width = '1900px';
const scrollRoom = document.createElement('div'); scrollRoom.style.height = '2200px'; document.querySelector('#trade').append(scrollRoom);
const dockedTop = dockedField.getBoundingClientRect().top;
window.scrollTo(0, 600);
await new Promise(resolve => setTimeout(resolve, 100));
check('fields stay at viewport top while scrolling', Math.abs(dockedField.getBoundingClientRect().top-dockedTop)<1 && Math.abs(dockedField.getBoundingClientRect().top-12)<1);
check('Show Filters stays visible while scrolling', actions.querySelector('.toggle-search-btn').getBoundingClientRect().top >= 0 && actions.getBoundingClientRect().bottom < window.innerHeight);
toggleChevron.classList.remove('collapsed');
check('opening filters while scrolled keeps toolbar docked', Math.abs(dockedField.getBoundingClientRect().top-12)<1 && Math.abs(actions.getBoundingClientRect().top-7)<1);
toggleChevron.classList.add('collapsed');
window.scrollTo(0,0);
await new Promise(resolve => setTimeout(resolve, 100));
check('hidden dropdown stays hidden', c('.multiselect__content-wrapper').display === 'none');
$('.minmax').focus();
check('input focus uses orange border', c('.minmax').borderTopColor === 'rgb(189, 137, 89)');
check('input focus has no extra ring', c('.minmax').outlineStyle === 'none' && c('.minmax').boxShadow === 'none');
check('dropdown existing border uses muted orange', c('.multiselect').borderTopColor === 'rgb(97, 72, 48)');
const row = $('.resultset > .row');
const beforeHoverHeight = row.getBoundingClientRect().height;
// A class with the same specificity exercises hover declarations in dump-dom.
const hoverStyle = document.createElement('style');
hoverStyle.textContent = style.textContent.replaceAll(':hover', '.fixture-hover');
document.head.append(hoverStyle);
const addStatFilter = document.createElement('button'); addStatFilter.textContent = '+ Add Stat Filter'; addStatFilter.className = 'fixture-hover'; leftFilters.append(addStatFilter);
const addStatGroup = document.createElement('button'); addStatGroup.textContent = '+ Add Stat Group'; addStatGroup.className = 'fixture-hover'; rightFilters.append(addStatGroup);
check('stat add buttons get blue hover', [addStatFilter, addStatGroup].every(button => getComputedStyle(button).backgroundColor === 'rgb(16, 23, 28)'));
row.classList.add('fixture-hover');
check('hover removes native grey card fill', c('.resultset > .row').backgroundColor === 'rgba(0, 0, 0, 0)' && c('.resultset .middle').backgroundColor === 'rgba(0, 0, 0, 0)' && c('.resultset .details').backgroundColor === 'rgba(0, 0, 0, 0)');
check('hover outlines entire item orange', c('.resultset > .row').outlineColor === 'rgb(189, 137, 89)' && c('.resultset > .row').outlineStyle === 'solid');
check('hover does not change card height', row.getBoundingClientRect().height === beforeHoverHeight);
const shadow = $('better-trading').attachShadow({mode:'open'});
shadow.innerHTML = '<style>.bt-panel{background:#010203;font-family:serif}</style><aside class="bt-panel">Bookmarks</aside>';
check('Better Trading shadow styling unchanged', getComputedStyle(shadow.querySelector('.bt-panel')).backgroundColor === 'rgb(1, 2, 3)' && getComputedStyle(shadow.querySelector('.bt-panel')).fontFamily === 'serif');
$('#results').textContent = JSON.stringify(checks);
'''.replace('CSS', json.dumps(css)).replace('DETAILS_HTML', json.dumps(live_details)).replace('TOOLBAR_HTML', json.dumps(toolbar_html))
page = '<!doctype html><html><head><style>' + baseline + '</style></head><body>' + markup + '<script type="module">' + checks + '</script></body></html>'
browser = os.environ.get('BT_TEST_BROWSER', r'C:\Program Files\Google\Chrome\Application\chrome.exe')
with tempfile.TemporaryDirectory(prefix='poe-site-theme-check-') as tmp:
    path = Path(tmp) / 'check.html'
    path.write_text(page, encoding='utf-8')
    run = subprocess.run([
        browser, '--headless=new', '--disable-gpu', '--no-first-run', '--window-size=2200,900',
        '--no-default-browser-check', f'--user-data-dir={Path(tmp) / "profile"}',
        '--dump-dom', '--virtual-time-budget=4000', path.as_uri(),
    ], capture_output=True, text=True, encoding='utf-8', timeout=45)
    match = re.search(r'<pre id="results">(.*?)</pre>', run.stdout, re.S)
    if not match or match.group(1) == 'pending':
        raise SystemExit('Browser checks did not complete.\n' + run.stderr[-1500:])
    result = json.loads(html.unescape(match.group(1)))
    print(json.dumps(result, indent=2))
    if not all(check['pass'] for check in result):
        raise SystemExit(1)

# Exercise actual viewport breakpoints with sidebar-sized space reserved on the right.
responsive_checks = r"""
const style = document.createElement('style'); style.textContent = CSS; document.head.append(style);
document.body.insertAdjacentHTML('afterbegin', ACCOUNT_HTML);
const trade = document.querySelector('#trade');
trade.style.width = (innerWidth - 405) + 'px';
if (innerWidth >= 2560) { trade.style.width = '1900px'; trade.style.marginLeft = '300px'; }
trade.innerHTML = TOOLBAR_HTML;
const field = trade.querySelector('.search-select');
const actions = trade.querySelector('.controls');
const rect = el => el.getBoundingClientRect();
const pinned = innerWidth >= 1280;
const checks = [];
const check = (label, pass) => checks.push({label, pass});
check('responsive pinning breakpoint', (getComputedStyle(field).position === 'fixed') === pinned);
if (pinned) {
  const inset = Math.min(400, Math.max(320, innerWidth * .18));
  check('responsive left inset', Math.abs(rect(field).left - inset) < 1);
  check('right edge avoids sidebar', Math.abs(rect(actions).right - rect(trade).right) < 1);
  const nodes = [field, ...trade.querySelectorAll('.status-select'), actions];
  check('controls fit available bounds', nodes.every(el => rect(el).width > 0 && rect(el).left >= inset - 1 && rect(el).right <= rect(trade).right + 1 && el.scrollWidth <= el.clientWidth + 1));
  check('search tags fill field', Math.abs(rect(field.querySelector('.multiselect__tags')).width - rect(field).width) < 2);
  check('search input fills tags', rect(field.querySelector('input')).width >= rect(field).width - 36);
  check('input fits field', rect(field.querySelector('input')).right <= rect(field).right);
  check('search field fills available span ' + JSON.stringify([rect(field).left,rect(field).right,rect(trade.querySelector('.status-select')).left,getComputedStyle(field).right,getComputedStyle(field).width]), rect(trade.querySelector('.status-select')).left - rect(field).right >= 0 && rect(trade.querySelector('.status-select')).left - rect(field).right <= 8);
  if (innerWidth >= 1600) {
    check('one compact toolbar row', Math.abs((rect(field).top + rect(field).height / 2) - (rect(actions).top + rect(actions).height / 2)) < 1);
    check('no second reserved panel row', getComputedStyle(trade.querySelector('.search-panel')).paddingTop === '0px');
  }
  check('field height unchanged', rect(field).height === 32);
  check('row layout unchanged', Math.abs(rect(actions).top - (innerWidth >= 1600 ? 7 : 42)) < 1);
  const accountRows = [...document.querySelectorAll('.row1, .row2, .linkBack')];
  check('account rows fixed and clear of toolbar', accountRows.every(el => getComputedStyle(el).position === 'fixed' && rect(el).right < rect(field).left));
  check('account rows do not overlap', rect(accountRows[0]).bottom <= rect(accountRows[1]).top && rect(accountRows[1]).bottom <= rect(accountRows[2]).top);
  check('logout form remains hidden', getComputedStyle(document.querySelector('.row2 form')).display === 'none');
  const before = accountRows.map(el => rect(el).top);
  document.body.style.minHeight = '2200px'; window.scrollTo(0, 500);
  check('account stays visible after scrolling', accountRows.every((el, i) => Math.abs(rect(el).top - before[i]) < 1));
  window.scrollTo(0, 0);
  const backdrop = getComputedStyle(trade, '::before');
  check('unified backdrop spans account and toolbar', parseFloat(backdrop.left) === 0 && parseFloat(backdrop.right) === 0 && parseFloat(backdrop.height) >= rect(document.querySelector('.linkBack')).bottom);
  check('backdrop stays below Better Trading panel', Number(backdrop.zIndex) < 1000);
  check('header matches item backing transparency', backdrop.backgroundColor === getComputedStyle(trade).backgroundColor);
  check('account rows share backdrop', accountRows.every(el => getComputedStyle(el).backgroundColor === 'rgba(0, 0, 0, 0)'));
}
document.querySelector('#results').textContent = JSON.stringify(checks);
""".replace('CSS', json.dumps(css)).replace('TOOLBAR_HTML', json.dumps(toolbar_html)).replace('ACCOUNT_HTML', json.dumps(account_html))
responsive_page = '<!doctype html><html><head><style>' + baseline + '</style></head><body><div id="trade"></div><pre id="results">pending</pre><script type="module">' + responsive_checks + '</script></body></html>'
for width in (1000, 1100, 1366, 1920, 2000, 2560, 3440):
    with tempfile.TemporaryDirectory(prefix='poe-responsive-check-') as tmp:
        path = Path(tmp) / 'check.html'
        path.write_text(responsive_page, encoding='utf-8')
        run = subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-first-run', f'--window-size={width},900', '--no-default-browser-check', f'--user-data-dir={Path(tmp) / "profile"}', '--dump-dom', '--virtual-time-budget=2000', path.as_uri()], capture_output=True, text=True, encoding='utf-8', timeout=45)
        match = re.search(r'<pre id="results">(.*?)</pre>', run.stdout, re.S)
        if not match or match.group(1) == 'pending':
            raise SystemExit(f'Responsive checks did not complete at {width}px')
        result = json.loads(html.unescape(match.group(1)))
        failures = [check for check in result if not check['pass']]
        print(f"{width}px: {len(result)} responsive checks, failures: {failures}")
        if failures:
            raise SystemExit(1)
