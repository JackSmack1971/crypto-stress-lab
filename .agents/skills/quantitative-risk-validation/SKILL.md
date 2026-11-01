---
name: quantitative-risk-validation
description: "Validate portfolio and stress-engine numerical behavior against deterministic fixtures, edge cases, units, and reproducibility requirements. Use when changing or auditing quantitative calculations; not for security-only reviews or unrelated documentation."
---

# Quantitative risk validation

Validate the browser application's quantitative calculations against explicit numerical evidence. Follow `AGENTS.md` and use only existing repository code and test conventions. This skill is implicit-invocation eligible; that label describes intended routing, not a guarantee that the runtime invokes it.

## 1. Locate the calculation contract

- Inspect `dist/engine.mjs`, its callers, fixtures, tests, and documented model assumptions before proposing expected results.
- Identify input and output units, accepted domains, rounding points, missing-data behavior, and error behavior.
- Treat imported portfolio JSON and persisted values as untrusted inputs. Do not infer validation from UI controls alone.

## 2. Build hand-computable deterministic fixtures

- Create small fixtures whose outputs can be calculated independently by hand; include at least one ordinary multi-asset case and one boundary case relevant to the changed calculation.
- State every input and expected output with units. Distinguish percentages (for example, `5%`) from fractional values (`0.05`) and identify USD amounts explicitly.
- Keep fixtures deterministic: no current time, randomness, network data, environment-dependent values, or implicit external state.
- Document material model assumptions and limits alongside the expected results. Do not present a simplified fixture as proof of real-world predictive accuracy.

## 3. Exercise edge cases and properties

Select cases that match the engine contract, including:

- Empty portfolio and zero total exposure.
- Zero weights and negative weights, including whether short positions are supported or rejected.
- `NaN`, positive/negative infinity, missing fields, and malformed numeric input from imports or persisted state.
- Rounding boundaries, aggregate rounding, and unit conversion boundaries.
- Invariants or metamorphic properties such as deterministic repeatability, scale consistency where mathematically expected, and valid bounds for normalized weights where applicable.

For every property, state its preconditions. Do not impose properties that conflict with documented model assumptions.

## 4. Verify and report

- Use the narrowest existing test or check that exercises the changed calculation. Do not add dependencies, weaken tests, or claim a check ran when it did not.
- Compare actual outputs with hand-computed expected values and meaningful tolerances; explain any tolerance in the engine's units.
- Record exact commands and outcomes. Separate code observations, executed evidence, assumptions, and unverified behavior.
- Report uncovered edge cases and model limitations. A passing fixture validates only the exercised calculation and inputs; it does not establish market accuracy or security assurance.
