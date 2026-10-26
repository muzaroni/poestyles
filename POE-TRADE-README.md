# PoE Trade Compact Dark

A separate Stylus theme for the official Path of Exile trade website. It uses translucent black sections, quiet separators, warm orange search accents and embedded JetBrains Mono.

## Install

1. Open **Stylus → Manage → Backup → Import**.
2. Choose `poe-trade-compact.stylus.json` and confirm **PoE Trade Compact Dark** is enabled.
3. Reload `https://www.pathofexile.com/trade/`.

This website theme works directly in Stylus. The existing Better Trading theme and bridge can remain enabled alongside it. The two styles have different names and variable prefixes, and this stylesheet does not select inside the extension's shadow root.

The URL prefixes include the main `trade` and `trade2` routes on `www.pathofexile.com` and `pathofexile.com`. Rules require the site's `#trade` root before changing the page canvas. Forums and other site pages are outside the URL scope.

## Pinned toolbar

On current Chrome/Brave browsers with CSS anchor positioning, the four original field/dropdown nodes and the controls are fixed at the top of the viewport. Show/Hide Filters stays accessible while scrolling, with the same docked layout in both filter states. The `.search-bar`, `.search-left` and `.search-right` wrappers keep their native document layout, including any expanded filter columns nested inside them; no parent grid or DOM reparenting is used.

At viewport widths of 1600px and above, the two blocks share one row. Between 1280px and 1599px they form two pinned rows. Below 1280px, or without anchor support, the native toolbar remains in document flow. The compact action area uses 224px on wide screens. The toolbar reserves `clamp(320px, 18vw, 400px)` on the left for the native header (345.6px at a 1920px viewport), while keeping its right edge anchored to the main trade area so it stays out of the Better Trading sidebar. The search field shrinks to fit; existing control heights remain unchanged; pinned layouts hide the native logo artwork while retaining a compact layout spacer. Space is reserved in the search panel to avoid covering its first filter rows.

The native account rows (`.row1` containing `.loggedInStatus`, `.row2` containing account links, and `.linkBack`) are fixed at the upper left on pinned layouts. Account links and the hidden logout form remain native. The logo artwork is hidden with `visibility: hidden`, preserving the header spacer so the navigation tabs stay below the dock. One continuous dark backdrop covers the account block and toolbar, using the same 76% black as the item area. At 1600px and above the header is 64px tall, the search controls share one row beside the account details, and no duplicate spacer is added inside the search panel.

The original controls remain the actual clickable Vue nodes. Native hidden toolbar copies remain hidden, including when filters open. Dropdowns retain their own positioned menus. This uses [CSS anchor positioning](https://developer.chrome.com/blog/anchor-positioning-api). The Better Trading Stylus Bridge userscript also scrolls smoothly to the top when **Show Filters** is clicked, so the expanded filters are visible. Update that script in Tampermonkey to get this behavior.

The toolbar keeps **Search** as text with a muted blue background. Live Search uses Google's Material Icons cell-tower glyph, yellow while idle and red while active. The Search action displays **Live...** while Live Search is active, keeping the toolbar on one row; the site's full status remains in the button for assistive technology. Show/Hide Filters uses a three-line sliders icon, and Clear uses a red X. The cell-tower glyph is embedded in the stylesheet under Google's [Apache 2.0 license](https://github.com/google/material-design-icons/blob/master/LICENSE), so it makes no font request. On wide screens, the three status selectors sit closer to the actions so the item search field can expand. The fixed bar uses slightly translucent black, the closed search bar no longer reserves an empty row, and a second action row inside expanded filters is hidden.

The toolbar uses the user-supplied DOM saved in `tests/fixtures/search-toolbar.html` (hidden option lists trimmed).

## Coverage

- Main PoE logo artwork hidden in pinned layouts while preserving its header space; native-flow layouts retain the compact logo.
- Native page artwork retained behind a 76% black translucent backing. Nested sections remain transparent to avoid stacking opacity.
- Filter columns reveal the same translucent main backing as item results. Very dark blue-gray headers (`#080e12`) have thin underlines and a `#10171c` hover. Buttons in the expanded pane, including Add Stat Filter and Add Stat Group, use a matching blue hover; toggle and remove icons retain their own styling.
- Native filter/input heights and alignment, with reduced inter-section spacing. Collapse wrappers retain their native zero-height state.
- Orange existing input/dropdown selection borders without an additional focus ring.
- Dark orange search button and selected dropdown options.
- Dark inputs and dropdowns with visible keyboard focus.
- Compact result image columns keep the website's native layout and positioning. This preserves image-left cards after switching from Live Search back to a manual search.
- Transparent result cards with an orange full-card hover/focus outline and no grey hover fill.
- Native copy/filter button artwork and icon fonts are preserved.
- Listing action buttons use compact dark styling. Pin is hidden at the user's request. Asking price, fee and conversion share the upper row. The account and Ignore Player sit below, with Travel to Hideout at the far right. Rows wrap on narrow cards. The indexed/listed-time metadata keeps its native positioning.
- Embedded JetBrains Mono, independent of installed-font detection.

Rarity headers, explicit/implicit modifier colors, currency images, sockets, online indicators, live-search state colors and contact-button state colors are not recolored. Pin is hidden by request; no other controls are hidden, and no script, search, trade, account or storage behavior is changed. Native responsive widths, filter expansion and dropdown positioning are retained.

## What was confirmed

The live website returned a security verification page to the inspection browser, so this first version was prepared from Better Trading's integration source and its captured HTML fixtures, at commit `e14745c6734c6bc95609c6e812b3f1444cbca215` of [Vali-98/better-trading](https://github.com/Vali-98/better-trading/tree/e14745c6734c6bc95609c6e812b3f1444cbca215).

| Selectors | Evidence under `src/integrations/poe-trade/` or `test/` |
| --- | --- |
| `#trade`, `.resultset > div.row[data-id]`, `.details`, `.price`, `.left`, `.middle` | `results.ts`, `copyItem.ts`, `snapshots.ts` |
| `.search-panel`, `.search-bar`, `.search-advanced-pane`, `.filter-group`, `.filter-group-body`, `.filter-title` | `searchPanel.ts`, `expandFilters.ts`, `searchInputs.ts` |
| `.filter`, `.multiselect`, `.multiselect__tags`, `.multiselect__input`, `.multiselect__content-wrapper`, `.multiselect__option--selected` | `fixtures/property-filters.html`, `search.ts` |
| `.search-btn`, `.clear-btn`, `.toggle-search-btn`, `.toggle-btn` | `search.ts`, `expandFilters.ts` |
| `.copy`, `.searchBy` | `copyItem.ts`, `results.css` |
| `.details .btns`, `.bt-pin-button`, `.btn-default` | `results.ts`, `lib/results/enhancers/pinning.ts` |
| `.item-popup__content`, `.item-popup__header-line`, `.itemRendered`, `.itemHeader`, `.itemName` | `fixtures/poe2-headhunter.html`, `itemIdentity.ts`, `itemText.ts` |

Outer `.container-fluid`, `.content` and `.wrapper` classes were visible in the earlier supplied DevTools screenshot. The dropdown's `__single`, `__select`, `__option--highlight` and `__option--disabled` selectors are conventional Vue Multiselect classes; their presence on the installed page remains to be checked in DevTools. Missing optional classes simply do not match.

The toolbar fields/action markup and the nested `.filter-group-header > .filter` structure were confirmed from user-supplied HTML. The exact current navigation-tab markup, account menus, modal dialogs and all bulk-exchange layouts were not confirmed, so this version does not add speculative selectors for them. The header's blue-gray surface and underline are applied to `.filter-group-header`; its nested `.filter` stays transparent. Broad rules over all group children are avoided because they can inflate collapsed wrappers. Website updates may change these selectors.

The listing footer structure was subsequently confirmed from the live `.details` HTML supplied by the user. An anonymized copy is saved in `tests/fixtures/listing-details.html`. The layout uses its `.price`, `[data-field="fee"]`, `.bt-equivalent-pricings`, `.character-name`, `.btn-group > .direct-btn`, and `button.ignore-btn` elements. No button is reparented or recreated, and expired Travel buttons remain disabled.

## Editing

`poe-trade-compact.user.css` is the source. Color variables are near the start of `body:has(#trade)`. The `--pt-panel-bg` variable controls the page backing opacity (currently `0.76`). The large `@font-face` data URL contains the font; leave it intact when editing colors or spacing. Its original file and SIL Open Font License are in `assets/`.

Run `node scripts/build-stylus-json.mjs` to regenerate both JSON imports after source changes. Reimport the website JSON into Stylus, or edit the installed website style directly for immediate changes.

Disable **PoE Trade Compact Dark** to restore the website's styling independently of Better Trading.

## Verification and first live check

The website theme is checked in headless Chrome against the repository's filter and PoE 2 item HTML fixtures. These checks exercise font loading, filter/dropdown/control styling, selected options, disabled control behavior, result styling, semantic color preservation and isolation from Better Trading's shadow root. They include checks that the section does not grow beyond native fixture height, input heights are unchanged, collapsed wrappers stay at zero, focus borders are orange without an extra ring, native body/wrapper and copy/filter icon artwork is retained, and the hover treatment uses a full-card orange outline without changing card height. They are not a substitute for a live website check.

Run `python scripts/check-site-theme.py` to rerun the fixture checks. The inspected source checkout must be at `.source-better-trading`; `BT_TEST_BROWSER` can specify an alternate Chromium executable.

After importing, check the search form, dropdown hover/selection, results, live-search controls, and any exchange page you use. If a section is still unthemed, inspect the element's classes and winning CSS rule or share a screenshot so it can be targeted precisely.

## Latest layout adjustment (0.9.27)

The search input and its inner tags now fill the available toolbar width, with the dropdown arrow at the far right. The continuous header backing sits below Better Trading (z-index 999 versus the panel's 1000), so it no longer dims the extension header. Reimport `poe-trade-compact.stylus.json` in Stylus and reload the trade page to apply this update.
