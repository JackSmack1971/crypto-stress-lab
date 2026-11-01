# Fast applicable-state checklist

Use as a final inspection aid, not a universal list of mandatory tests. Detailed selection: `verification-matrix.md`.

- Relevant loading, empty, success and failure states are observable.
- Modified controls have semantic roles, labels, keyboard paths and focus visibility.
- Forms expose errors, busy state and duplicate-submit protection if mutations occur.
- Changed layout is examined at affected narrow/wide viewports and with challenging content.
- Requests handle failure, retry/stale/cancel paths when applicable.
- Existing supported frameworks, browsers, tokens and global styles remain respected.
- Focused checks and available rendered observations support each material completion claim.
- No unrelated changes, secrets, unjustified dependencies or mechanically accepted snapshots remain.
