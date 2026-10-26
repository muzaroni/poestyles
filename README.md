# Path of Exile themes for Stylus

Two dark themes for Path of Exile: **Better Trading Compact Dark** styles the Better Trading extension panel, and **PoE Trade Compact Dark** styles the official trade website.

## Install the PoE trade website theme

1. Install the [Stylus browser extension](https://github.com/openstyles/stylus).
2. Open [PoE Trade Compact Dark](https://raw.githubusercontent.com/muzaroni/poestyles/master/poe-trade-compact.user.css).
3. On the Stylus page, choose **Install style** and leave **Check for updates** enabled.

## Install the Better Trading extension theme

This theme needs the [Better Trading extension](https://github.com/Vali-98/better-trading), Stylus, and Tampermonkey.

1. Install the [Better Trading Stylus Bridge](https://raw.githubusercontent.com/muzaroni/poestyles/master/better-trading-stylus-bridge.user.js) in Tampermonkey.
2. Open [Better Trading Compact Dark](https://raw.githubusercontent.com/muzaroni/poestyles/master/better-trading-compact.user.css).
3. On the Stylus page, choose **Install style** and leave **Check for updates** enabled.
4. Reload the Path of Exile trade page.

The bridge lets Stylus theme the extension's panel. Both themes are optional and can be managed or removed in their respective extensions.

## Manual Stylus import

The `.stylus.json` files are backups for **Stylus → Manage → Backup → Import**. Styles installed from these backup files do not use the hosted UserCSS update links; install from the links above to receive updates through Stylus.

## Project files

The `.user.css` files are the editable sources. `scripts/build-stylus-json.mjs` regenerates the import backups from those sources. The Better Trading bridge is distributed as a Tampermonkey userscript.
