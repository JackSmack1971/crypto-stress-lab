# Responsive and visual verification

Load when changing layout, CSS, typography, global tokens, themes or display density.

1. Identify supported breakpoints and browser targets from the project; do not impose arbitrary universal breakpoints.
2. Inspect changed UI at representative narrow and wide sizes and any breakpoint affected by the diff; check horizontal overflow, content clipping, touch reachability and visible focus.
3. Exercise long labels, empty content, large data, and localization or zoom where they can invalidate the changed layout.
4. Inspect loading/error/empty states rather than judging only populated happy-path screenshots.
5. For screenshot baseline changes, identify what moved and why; don't bulk-approve diffs. Compare like-for-like viewport, fonts, data and animations where feasible.
6. Check shared tokens/global styles on representative consumers. Stop if broad visual effects cannot be isolated and report the unresolved impact.

A rendered screenshot establishes appearance at the observed state and width only. It does not establish responsive correctness at untested widths or interaction correctness without interaction evidence.
