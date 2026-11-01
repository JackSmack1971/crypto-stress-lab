# Crypto Stress Lab

A standalone, browser-only crypto portfolio risk stress tester. Enter asset allocations and hypothetical shocks, then compare portfolio losses, correlation sensitivity, and concentration effects.

## Features

- One to twelve editable assets, with portfolio weights, annual volatility assumptions, and event shocks.
- Broad selloff, liquidity squeeze, stablecoin depeg, relief rally, and custom scenarios.
- Adjustable shock intensity, baseline/stressed common correlation, and risk horizon.
- Scenario return and drawdown comparisons, volatility sensitivity chart, allocation chart, and asset-level attribution.
- Reverse stress testing by portfolio, asset, or group, with a target loss in percent or USD and an explicit unreachable result.
- Sensitivity heatmap across stressed correlation and shock intensity for horizon volatility, 99% normal-model downside, or scenario return.
- HHI, effective position count, equal-weight comparisons, and 95%/99% normal-model downside and expected shortfall using stressed volatility.
- Explicit weight normalization and validation, browser-local input persistence, and CSV export.
- Deterministic, versioned portfolio JSON export and strict import with preview and explicit replacement confirmation.
- Responsive layouts for phones, tablets, and desktop browsers.

Static HTML, CSS, and ES modules. No runtime dependencies; one dev dependency for browser tests. No build step, market feed, wallet connection, account connection, analytics, or trading functionality.

## Run locally

The app uses ES modules: serve it over HTTP rather than opening index.html as a file.

With Python 3 installed, run this from the repository root:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8000 in your browser. On systems where Python 3 is named `python3`, use that command instead.

Any static web server can serve the `dist` folder without installing app dependencies.

## Run checks

With a current Node.js LTS release installed:

```sh
npm test
npm run check
npm run e2e
```

Run `npm ci` to install the browser-test dependency and `npx playwright install chromium` once to install its browser. The Node test suite contains 65 tests, including persistence restore, strict portfolio JSON import/export, validation of malformed assets, CSV row generation, escaping and formula neutralization, 300 deterministic portfolio fixtures compared with explicit covariance matrix multiplication, reverse-stress and sensitivity fixtures and properties, and Gaussian tail-risk checks. The Playwright suite exercises the app in Chromium. Browser verification details are recorded in VERIFICATION.md.

Set `PW_CHROME_PATH` to an installed Chrome or Chromium executable to use it instead of running `npx playwright install chromium` (for example, `PW_CHROME_PATH=/usr/bin/chromium npm run e2e`).

## Transfer to GitHub

1. Unzip this archive. The `crypto-stress-lab` folder is the repository root.
2. Create an empty **private** GitHub repository.
3. Upload the contents of that folder, including `.gitignore`, or push with Git:

```sh
git init -b main
git add .
git commit -m "Initial import of Crypto Stress Lab"
git remote add origin https://github.com/YOUR-USERNAME/crypto-stress-lab.git
git push -u origin main
```

Replace the remote URL with your own empty repository's URL. Git history, remote settings, credentials, and active Sites deployment identity are excluded from this export. This archive contains source files, not an initialized Git repository.

## Hosting and privacy

The existing private Sites deployment remains separate and unchanged:
https://crypto-stress-lab-jack-ef081f.jacksmack.chatgpt.site/

This export does **not** include the platform's authentication gate. The original app's “Private” and “Owner-only access” interface labels describe its Sites environment; they do not enforce access control when the static files are served elsewhere. A private source repository alone does not make an independently hosted website private. Configure authentication on any standalone host before entering real portfolio data or making it accessible beyond localhost.

The static hosting directory is `dist`; no build command is required. Deployment and publication remain separate steps; no automatic deployment workflow is included.

## Model and limitations

Weights must total 100%; the model covers long-only spot portfolios. Effective asset shock = base shock × intensity, floored at −100% for each asset. Portfolio return is the weighted sum of effective shocks. Scenario P&L = starting value × return; ending value = starting value + P&L. Scenario drawdown is max(0, −return), a one-step scenario loss rather than maximum peak-to-trough drawdown over a price path.

All off-diagonal asset correlations use one common value rho between 0 and 1. Annual variance = (1 − rho) × sum((weight × annual volatility)^2) + rho × (sum(weight × annual volatility))^2. This produces a valid covariance matrix. Horizon volatility = annual volatility × sqrt(days / 365). Correlation and horizon affect model risk but do not change the deterministic event shocks.

Normal-model downside and expected shortfall use only stressed horizon volatility and assume zero expected return with normally distributed returns. Downside at confidence c is the loss threshold at that confidence level: zᶜ × σ. Expected shortfall is the average loss given that the threshold is exceeded, φ(zᶜ) / (1 − c) × σ, and is therefore at least as large as downside. Both are one-sided losses expressed as a fraction of starting portfolio value, with static positions and common-ρ covariance. The one-sided z-scores are 1.6448536269514722 at 95% and 2.3263478740408408 at 99%. Fat tails are likely understated, and deterministic scenario shocks are excluded. These estimates are not a maximum loss or a forecast, are not feasible spot-loss bounds, and can exceed 100%. No simulation is used.

Reverse stress testing solves for the instantaneous uniform price shock to selected assets that reaches a positive target loss, entered as a portfolio percentage or USD amount. Portfolio mode includes every holding, including stablecoins and cash; asset and group modes include only their selected holdings, while all other assets remain unchanged. The model assumes long-only spot positions and enforces a −100% price floor. A target is unreachable when the selected exposure cannot lose enough value, including an empty selection or zero-weight selection. Reverse stress has no dependence on correlation, horizon, volatility, intensity, or per-asset base shocks. It excludes fees, slippage, liquidity constraints, and price-path effects. Reverse-stress controls are kept in memory for the current page session and are not persisted.

The sensitivity heatmap varies stressed correlation rho from 0 to 1 in 0.1 steps across columns and shock intensity from 0 to 3 in 0.25 steps down rows. Horizon volatility is stressed portfolio volatility times sqrt(days / 365), shown as a fraction of starting value; 99% model downside (VaR) is 2.3263478740408408 times that volatility, also a fraction; scenario return is the weighted sum of current per-asset base shocks multiplied by intensity, with a −100% per-asset floor. Volatility and VaR are flat across intensity; scenario return is flat across correlation. The marker identifies the nearest grid point to current settings; the exact current metric is shown separately. The heatmap varies stressed correlation only; baseline correlation remains unchanged, and CSV output is unaffected. The same static long-only spot and Gaussian-model limitations described above apply.

Concentration uses HHI = sum(weight^2) and effective positions = 1 / HHI. The equal-weight comparison includes every listed asset, including zero-weight assets. Risk shares are Euler variance contributions divided by total stressed variance; zero total variance has no defined share.

Sample inputs are illustrative assumptions. Fees, slippage, liquidity, leverage, liquidation, taxes, rebalancing, fat tails, and intraperiod paths are outside this model. The in-app “Behind the numbers” section explains the formulas.

Inputs persist in browser-local storage when available. Invalid edits do not overwrite the last valid saved state. CSV exports include the assumptions and calculated results; tail-risk metrics are appended after the existing Limitations row, and all existing CSV rows remain unchanged and in the same order. Formula-like user strings are neutralized. Large P&L summary values use compact notation while exact values remain available in details, attribution, and exports.

## Portfolio JSON import and export

JSON files use an independent envelope with `schema: "crypto-stress-lab/portfolio"`, integer `schemaVersion: 1`, and a `portfolio` object. The portfolio has exactly these fields:

| Field | Meaning and units |
| --- | --- |
| `value` | Starting portfolio value in USD, from 1 to 1,000,000,000,000 |
| `days` | Risk horizon in whole days, from 1 to 365 |
| `baseCorrelation` | Baseline common correlation as a fraction from 0 to 1 |
| `stressCorrelation` | Stressed common correlation as a fraction from 0 to 1 |
| `multiplier` | Shock intensity as a multiplier from 0 to 3 |
| `preset` | `selloff`, `liquidity`, `depeg`, `rally`, or `custom` |
| `assets` | 1–12 asset objects with the fields below |
| `assets[].id` | Unique local asset identifier: 1–64 ASCII letters, digits, underscores, or hyphens |
| `assets[].symbol` | Unique 1–12 character asset label; control characters are rejected |
| `assets[].group` | One of `bitcoin`, `ethereum`, `altcoin`, `stable`, or `cash` |
| `assets[].weight` | Portfolio allocation in percent units from 0 to 100; totals must be 100% within the app's existing tolerance |
| `assets[].volatility` | Annual volatility assumption in percent units from 0 to 300 |
| `assets[].shock` | Base scenario shock in percent units from −100 to 300 |

The exported JSON excludes the local-storage `version` key, derived returns and risk values, and UI-only reverse-stress and heatmap selections. It is independent of the persisted-state schema; applying an import wraps the portfolio in the existing local-storage `version: 1` shape. Export uses fixed key order, two-space indentation, a final newline, and a fixed filename, with no timestamp, so identical inputs produce byte-identical JSON.

Import accepts only this exact envelope and schema version 1. Unknown and future versions fail safely; supporting a later schema requires an explicit migration and tests. The parser checks a 65,536-byte UTF-8 limit before JSON parsing, requires fatal UTF-8 decoding, strips exactly one leading BOM, uses a strict field allowlist with no type coercion, and reports fix-oriented errors. Imported content is previewed and changes the portfolio only after explicit confirmation; cancel, Escape, malformed input, and invalid input do not update in-memory or saved state. Preview text is inserted as text, with no HTML interpretation or network access. The file is not authenticated or signed, and JavaScript `JSON.parse` retains the last of duplicate object keys, so duplicate keys cannot be reliably detected after parsing. CSV formula neutralization still applies to formula-like symbols in CSV exports.

## Files

```text
dist/
  index.html             Application interface
  style.css              Responsive dark theme
  app.mjs                Interactions, charts, saved inputs, CSV export
  engine.mjs             Pure portfolio calculations and input validation
  persistence.mjs        Saved-state restore, CSV, and portfolio JSON helpers
tests/
  engine.test.mjs        Deterministic calculation tests
  engine.reverse.test.mjs Reverse-stress fixtures and properties
  engine.sensitivity.test.mjs Correlation and intensity sensitivity grid tests
  persistence.test.mjs   Persistence, malformed-state and CSV tests
  portfolio-json.test.mjs Strict versioned portfolio JSON tests
package.json             Unit-test, syntax-check, and browser-test commands
package-lock.json        Pinned browser-test dependency tree
playwright.config.mjs    Chromium smoke-test configuration
e2e/                     Local static server and browser smoke tests
.gitignore               Local data, environment, and platform exclusions
README.md                Setup, GitHub transfer, model, and privacy notes
VERIFICATION.md          Original implementation verification record
```

## Provenance

Exported from the verified Sites source commit: `c5ec9687fe49f7e7bc27229fb45e9c7ac5b46698`.
Persistence and CSV helpers and their tests were added after export; other application and test source files are unchanged from that commit. This standalone README and .gitignore are export additions. The production deployment archive and internal screenshot are excluded because they are not required to run or maintain the source repository.
