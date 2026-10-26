"""Check the bridge in headless Chrome without the Better Trading extension.

Run: python scripts/check-bridge.py
Uses the inspected source checkout for the original panel CSS when present.
Creates a temporary browser profile and leaves the user's Chrome profile alone.
"""
from pathlib import Path
import html
import json
import os
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
theme = json.loads((root / 'better-trading-compact.stylus.json').read_text())[0]['sections'][0]['code']
bridge = (root / 'better-trading-stylus-bridge.user.js').read_text()
source = root / '.source-better-trading/src/styles/panel.css'
if not source.exists():
    raise SystemExit('Place the inspected Better Trading source at .source-better-trading first.')
base = re.sub(r'^@import[^\n]+\n', '', source.read_text(), flags=re.M)
checks = r'''
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const results = [];
function check(label, value) { results.push({label, pass: Boolean(value)}); }
const theme = document.createElement('style');
theme.id = 'stylus-123'; theme.className = 'stylus'; theme.textContent = THEME;
document.head.append(theme);
const localFonts = await document.fonts.load('12px "BT JetBrains Mono"');
check('embedded JetBrains Mono loads', localFonts.length > 0 && localFonts.every(font => font.status === 'loaded'));
const unrelated = document.createElement('unrelated-ui');
document.body.append(unrelated);
const unrelatedRoot = unrelated.attachShadow({mode:'open'});
unrelatedRoot.innerHTML = '<div class="bt-panel" style="background:rgb(3,4,5)">Unrelated</div>';
const host = document.createElement('better-trading');
document.body.append(host);
const trade = document.createElement('div');
trade.id = 'trade';
trade.innerHTML = '<section class="search-panel"><div class="controls"><button class="livesearch-btn"><span>Activate Live Search</span></button><button class="search-btn"><span>Search</span></button></div></section>';
document.body.append(trade);
const shadow = host.attachShadow({mode:'open'});
shadow.innerHTML = '<style>*,::before,::after{box-sizing:border-box}'+BASE+'</style><aside class="bt-panel"><nav class="bt-tabs"><button aria-pressed="true">Bookmarks</button></nav><section class="bt-bookmarks"><div class="bt-folder"><header class="bt-folder-header"><button class="bt-folder-title">Folder</button><details class="bt-menu"><summary>...</summary><div><button>Edit</button></div></details><button class="bt-drag">Drag</button></header><div class="bt-trade-row"><a href="#">Bookmark</a><details class="bt-menu"><summary>...</summary><div><button>Edit</button></div></details><button class="bt-drag">Drag</button></div></div></section></aside>';
const originalSheet = new CSSStyleSheet();
originalSheet.replaceSync('.bt-panel { --original-preserved: yes; }');
shadow.adoptedStyleSheets = [originalSheet];
await pause(1500);
const panel = shadow.querySelector('.bt-panel');
check('theme enters late open shadow root', getComputedStyle(panel).backgroundColor === 'rgb(0, 0, 0)');
check('bookmark link uses JetBrains Mono alias', getComputedStyle(shadow.querySelector('.bt-trade-row > a')).fontFamily.startsWith('"BT JetBrains Mono"'));
check('unrelated root unchanged', getComputedStyle(unrelatedRoot.querySelector('div')).backgroundColor === 'rgb(3, 4, 5)' && unrelatedRoot.adoptedStyleSheets.length === 0);
check('page unchanged', getComputedStyle(document.querySelector('#page-button')).backgroundColor === 'rgb(7, 8, 9)');
check('extension stylesheet preserved', shadow.adoptedStyleSheets.includes(originalSheet));
check('compact navigation', shadow.querySelector('.bt-tabs button').getBoundingClientRect().height === 30);
const activeTab = getComputedStyle(shadow.querySelector('.bt-tabs button'));
check('active tab uses underline only', activeTab.backgroundColor === 'rgba(0, 0, 0, 0)' && activeTab.borderBottomWidth === '4px' && activeTab.borderBottomColor === 'rgb(189, 137, 89)');
check('warm buttons use darker surface', getComputedStyle(panel).getPropertyValue('--bt-orange-bg').trim() === '#211911');
const rowHeight = shadow.querySelector('.bt-trade-row').getBoundingClientRect().height;
check('compact bookmark row', rowHeight >= 26 && rowHeight <= 28);
check('compact folder header', shadow.querySelector('.bt-folder-header').getBoundingClientRect().height === 32);
check('folder header matches stat-filter blue', getComputedStyle(shadow.querySelector('.bt-folder-header')).backgroundColor === 'rgb(8, 14, 18)');
shadow.querySelector('.bt-folder-title').setAttribute('aria-expanded', 'true');
check('open folder header is brighter', getComputedStyle(shadow.querySelector('.bt-folder-header')).backgroundColor === 'rgb(18, 33, 43)');
shadow.querySelector('.bt-folder-title').setAttribute('aria-expanded', 'false');
check('drag touch behavior preserved', getComputedStyle(shadow.querySelector('.bt-drag')).touchAction === 'none');
check('CSS rules parse', theme.sheet.cssRules.length >= 55);
theme.textContent = THEME.replace('--bt-bg: #000000;', '--bt-bg: #123456;');
await pause(1300);
check('Stylus edits update theme', getComputedStyle(panel).backgroundColor === 'rgb(18, 52, 86)');
theme.remove();
await pause(1300);
check('removing style restores original', getComputedStyle(panel).backgroundColor === 'rgba(10, 10, 10, 0.8)' && shadow.adoptedStyleSheets.length === 1);
const adopted = new CSSStyleSheet();
adopted.replaceSync(THEME);
document.adoptedStyleSheets = [adopted];
await pause(1300);
check('adopted stylesheet mode', getComputedStyle(panel).backgroundColor === 'rgb(0, 0, 0)');
adopted.replaceSync('');
await pause(1300);
check('CSSOM clearing removes theme', shadow.adoptedStyleSheets.length === 1);
document.querySelector('#results').textContent = JSON.stringify({results, rowHeight});
'''
checks = checks.replace('THEME', json.dumps(theme)).replace('BASE', json.dumps(base))
page = '<!doctype html><html><head></head><body><button id="page-button" style="background:rgb(7,8,9)">Page</button><pre id="results">pending</pre><script>' + bridge + '</script><script type="module">' + checks + '</script></body></html>'
browser = Path(os.environ.get('BT_TEST_BROWSER', r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
with tempfile.TemporaryDirectory(prefix='bt-theme-check-') as tmp:
    path = Path(tmp) / 'check.html'
    path.write_text(page, encoding='utf-8')
    run = subprocess.run([
        str(browser), '--headless=new', '--disable-gpu', '--no-first-run',
        '--no-default-browser-check', f'--user-data-dir={Path(tmp) / "profile"}',
        '--dump-dom', '--virtual-time-budget=9500', path.as_uri(),
    ], capture_output=True, text=True, encoding='utf-8', timeout=45)
    match = re.search(r'<pre id="results">(.*?)</pre>', run.stdout, re.S)
    if not match or match.group(1) == 'pending':
        raise SystemExit('Browser checks did not complete.\n' + run.stderr[-1500:])
    result = json.loads(html.unescape(match.group(1)))
    print(json.dumps(result, indent=2))
    if not all(check['pass'] for check in result['results']):
        raise SystemExit(1)
