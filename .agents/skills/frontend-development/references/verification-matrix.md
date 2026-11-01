# Verification selection and evidence

Load when selecting checks, deciding whether UI behavior is verified, or diagnosing incomplete results. Use commands provided by the repository, not illustrative names below.

| Change class | Minimum discriminating evidence | Expand when |
|---|---|---|
| Pure copy or local visual style | Render target route/component at affected widths; inspect overflow and visual result | Shared tokens/global selectors or screenshot diff show wider effects |
| Component logic, state or interaction | Focused behavior test: action -> visible result, with failure/edge state if reachable | Shared component used across routes or failures indicate integration risk |
| Forms and data mutation | Validation, submit success/failure, disabled/pending, duplicate-submit behavior; safe mock or sandbox API | Real backend contract, auth or mutation semantics changed |
| Data fetching, caching, routing | Loading/empty/error/success and stale/cancel behavior as applicable; route or integration check | Cross-route navigation or shared fetch layer changes |
| Accessibility interaction | Keyboard traversal, focus movement/return, accessible names/states; appropriate automated scan | Composite widget or shared primitives affected |
| Global CSS/design system | Representative affected routes and viewport range, plus relevant visual regression checks | Browser support, typography, layout, or theme contracts changed |
| Build/config or dependency | Existing repository lint/type/build/tests impacted; inspect resulting bundle/config | Production runtime or framework behavior changed |

## Evidence order and limitations

- Establish red/green baseline if the affected tests are already runnable; don't modify fixtures merely to suppress red.
- Prefer observable assertions (role/name, content, navigation, state and focus) to private component implementation.
- Browser evidence must name actual route, action/state, viewport and observation; a test environment cannot establish live-service behavior.
- Screenshot comparison requires inspection of changed areas, baseline provenance, and acceptance reason. A new baseline alone is not a pass.
- Accessibility scans detect subsets of issues; supplement with keyboard and focus checks on modified controls.
- Performance improvements require measured comparable before/after conditions; no measured gain means no performance claim.
- An unavailable check is not passed. Use alternate evidence, specify the missing check, and calibrate completion accordingly.
