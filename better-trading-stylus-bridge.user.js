// ==UserScript==
// @name         Better Trading Stylus Bridge
// @namespace    local.better-trading.compact
// @version      0.2.5
// @description  Apply Better Trading's Stylus theme and support the trade page's pinned filter toolbar.
// @match        https://www.pathofexile.com/trade*
// @match        https://pathofexile.com/trade*
// @run-at       document-idle
// @grant        none
// @noframes
// ==/UserScript==

(() => {
  'use strict';

  const hostSelector = 'better-trading';
  const themeSelector = ':host(better-trading)';
  const states = new Map();
  let queued = false;

  // The pinned toolbar can be clicked far below the search panel. On opening
  // the native filters, bring their first rows into view. Capture the click
  // before Vue changes the button from Show Filters to Hide Filters.
  document.addEventListener('click', (event) => {
    const button = event.target.closest?.('#trade button.toggle-search-btn');
    if (!button || !button.querySelector('.chevron.collapsed')) return;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, true);

  // Keep conditional groups intact, but copy only rules explicitly marked for
  // Better Trading. No page rules or unrelated Stylus themes enter the panel.
  function extractRules(rules) {
    const output = [];
    for (const rule of rules) {
      if (rule.type === CSSRule.STYLE_RULE) {
        // The theme uses flat rules and marks every selector in each list.
        // Reject mixed lists rather than copying unmarked page selectors.
        const selectors = rule.selectorText.split(',');
        if (selectors.every((selector) => selector.trim().startsWith(themeSelector))) {
          output.push(rule.cssText);
        }
      } else if (rule.cssRules && rule.type !== CSSRule.KEYFRAMES_RULE) {
        const nested = extractRules(rule.cssRules);
        if (nested) {
          output.push(`${rule.cssText.slice(0, rule.cssText.indexOf('{'))}{${nested}}`);
        }
      }
    }
    return output.join('\n');
  }

  function readTheme() {
    const output = [];
    // Reading both forms supports ordinary Stylus style tags and its optional
    // constructed stylesheet injection. Cross-origin sheets are safely skipped.
    const sheets = new Set([...document.styleSheets, ...document.adoptedStyleSheets]);
    for (const sheet of sheets) {
      if (sheet.disabled) continue;
      try {
        const css = extractRules(sheet.cssRules);
        if (!css) continue;
        const media = sheet.media.mediaText;
        output.push(media && media !== 'all' ? `@media ${media}{${css}}` : css);
      } catch (error) {
        // Browser-owned and cross-origin stylesheets need not be readable.
        if (error.name !== 'SecurityError') console.warn('[BT theme bridge]', error);
      }
    }
    return output.join('\n');
  }

  function applyTheme(root, css) {
    let state = states.get(root);
    if (!state) {
      state = { sheet: null, style: null, css: null };
      states.set(root, state);
      try {
        state.sheet = new CSSStyleSheet();
        state.sheet.replaceSync('');
      } catch {
        // Fallback for browsers without constructed stylesheets.
        state.style = document.createElement('style');
        state.style.dataset.betterTradingStylusBridge = '';
      }
    }

    if (state.sheet) {
      if (state.css !== css) state.sheet.replaceSync(css);
      const sheets = root.adoptedStyleSheets.filter((sheet) => sheet !== state.sheet);
      const previous = root.adoptedStyleSheets;
      // Re-append only when necessary, preserving the extension's own sheets.
      if (css && previous.at(-1) !== state.sheet) root.adoptedStyleSheets = [...sheets, state.sheet];
      if (!css && previous.includes(state.sheet)) root.adoptedStyleSheets = sheets;
    } else {
      if (state.css !== css) state.style.textContent = css;
      if (css && root.lastChild !== state.style) root.append(state.style);
      if (!css) state.style.remove();
    }
    state.css = css;
  }

  function sync() {
    queued = false;
    const hosts = document.querySelectorAll(hostSelector);
    const active = new Set();
    let css;
    for (const host of hosts) {
      const root = host.shadowRoot;
      if (!root || !root.querySelector('.bt-panel')) continue;
      active.add(root);
      css ??= readTheme();
      applyTheme(root, css);
    }
    for (const root of states.keys()) {
      if (!active.has(root)) {
        applyTheme(root, '');
        states.delete(root);
      }
    }
  }

  function scheduleSync() {
    if (queued) return;
    queued = true;
    // Timers also run when the trade page is in a background tab.
    setTimeout(sync, 50);
  }

  // Detect style-tag edits and panel mounting. The interval also catches
  // CSSOM/adoptedStyleSheets updates and extension-created roots attached later,
  // which do not emit ordinary DOM mutation records.
  const observer = new MutationObserver(scheduleSync);
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ['disabled', 'media'],
  });
  setInterval(scheduleSync, 1000);
  sync();
})();
