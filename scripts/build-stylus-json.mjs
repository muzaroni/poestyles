// Run: node scripts/build-stylus-json.mjs
// The .user.css file is the source of truth for the Stylus backup import.
import { readFileSync, writeFileSync } from 'node:fs';

const themes = [
  ['better-trading-compact', 'Better Trading Compact Dark'],
  ['poe-trade-compact', 'PoE Trade Compact Dark'],
];
for (const [file, name] of themes) {
const source = new URL(`../${file}.user.css`, import.meta.url);
const output = new URL(`../${file}.stylus.json`, import.meta.url);
const css = readFileSync(source, 'utf8');
const version = css.match(/^@version\s+(\S+)/m)?.[1];
if (!version) throw new Error(`Missing @version in ${file}.user.css`);
const wrapper = css.indexOf('@-moz-document');
const start = css.indexOf('{', wrapper);
const end = css.lastIndexOf('}');
if (wrapper < 0 || start < 0 || end <= start) throw new Error('Missing UserCSS URL wrapper.');

const styles = [{
  name: `${name} v${version}`,
  version,
  enabled: true,
  sections: [{
    code: css.slice(start + 1, end).trim(),
    urls: [],
    urlPrefixes: ['https://www.pathofexile.com/trade', 'https://pathofexile.com/trade'],
    domains: [],
    regexps: [],
  }],
}];
writeFileSync(output, JSON.stringify(styles, null, 2) + '\n');
console.log(`Updated ${file}.stylus.json`);
}
