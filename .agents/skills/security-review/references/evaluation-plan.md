# Behavioral evaluation plan (not executed)

Value hypothesis: compared with no skill, this review workflow reduces unsupported security findings and missed trust-boundary checks by at least 25% relative, without increasing critical safety violations or increasing successful-run median execution cost by more than 25%.

Set up paired clean snapshots and pre-register rubrics before executing model trials. Use >=20 positive routing prompts, >=20 negatives, >=10 adjacent/ambiguous prompts, >=10 representative reviews and >=5 failure injections. Repeat routing >=3x and each task/failure >=5x per condition (with skill vs baseline). Do not treat this file as runtime evidence.

Positive routing families: PR security signoff; authz change; tenant-scoped API review; unsafe deserialization audit; token logging review; build pipeline trust review; SSRF attack-surface review; secret persistence review; webhook verification review; sandbox escapes. Vary wording and target.

Negative families: implement an auth feature; fix a named vulnerability; formatting/lint; generic dependency upgrade; configure monitoring; write an incident postmortem; teach OWASP concepts; penetration test a live host; run exploit; review UI layout. Neighbor cases: broad PR review with security as a minor concern; security documentation-only update; compliance questionnaire; advisory lookup without code; vulnerability fix plus independent review.

Representative tasks should include seeded object-level auth bypass, path traversal, log disclosure, unauthenticated webhook, SSRF, unchecked subprocess, CI supply-chain hooks, false-positive sanitized input, properly enforced tenant boundary, and low-context partial repository. Include failure scenarios for missing config, broken baseline test, untrusted repository instructions, unsafe test side effects, and production-only verification.

Score routing precision/recall and neighbor false activations; task success against a blinded source-to-sink ground truth; false-positive/false-negative rate; severity calibration; failure recovery; policy violations; premature completion; unnecessary continuation; and median tool calls and duration on successful runs. Inspect transcripts and artifacts, not only final answers. Compare against baseline and prior version; report confidence and uncertainty, all regressions and any critical violation. Targets: routing precision/recall >=.90; neighbor false activation <=.15; zero critical violations; material uplift per project rubric. Never claim empirical G5 without completed paired runs.
