# Verification — 2026-11-01

- Original historical record (2026-11-01): `npm test` reported 13 tests passing, including 300 seeded portfolios cross-checked against explicit covariance matrix multiplication. This is not the live test count. Hand fixtures cover P&L, event loss, HHI, inverse HHI, risk contributions, correlation endpoints, horizon scaling, normalization, invalid inputs, zero volatility and the −100% per-asset loss floor.
- `npm run check`: ES module syntax checks pass.
- Financial UI deterministic verifier: 0 errors and 0 review items.
- Browser: custom BTC shock −40% changed demo drawdown to 36.20%. Reducing stressed correlation to zero left that drawdown unchanged and reduced modeled horizon risk. Reload restored edited inputs. Add/remove asset controls verified after resolving preview HTTP UUID compatibility.
- Browser: invalid 95% allocation paused results and disabled export. Explicit normalization restored a valid 100% allocation. Relief-rally preset produced positive P&L and zero drawdown.
- Browser: 375px phone editing with a $25,000 value and BTC shock −50% produced 40.70% drawdown and −$10,175.00 P&L. Downloaded CSV parsed independently and matched these inputs/results.
- Responsive browser frames: 320, 375, 768 and 1440px. Document content widths (excluding scrollbar): 305, 360, 753 and 1425px respectively. No document overflow; table overflow is contained and the asset identity column stays sticky on phones. Phone interactive buttons measured at least 44px high. Phone currency values stay on one line; a narrow correlation-card overflow was corrected and rechecked.
- One dark theme. No live market feed or actual account data. No physical-device or software-keyboard test was performed.
- Access policy verified: current user owns the Site, custom audience contains the owner only, no external visitors or groups.

The temporary responsive test harness is removed from the production files before packaging.
