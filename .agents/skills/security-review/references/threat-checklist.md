# Surface-triggered threat checklist

Use only the sections implicated by entry points, sinks, or privilege boundaries. Every question is a hypothesis to investigate, not a finding.

## Untrusted input and output
- Can HTTP/API, message, file, URL, environment, model/tool, or persisted data reach SQL/NoSQL queries, shell commands, templates, HTML, serializers, interpreters, or file paths? Identify concrete encoding/parameterization at the sink.
- Are validation, type/size bounds, path canonicalization and upload handling enforced server-side? Are output encoding and content-type constraints appropriate to the actual context?
- Can SSRF access metadata/private networks through redirect, DNS, scheme or port changes? Are redirects, egress and URL resolution controlled where relevant?

## Identity and authorization
- Where is the authenticated principal established, and where does **each** object/tenant/role permission decision execute? Check direct and indirect entry paths, background jobs, caches, GraphQL/resolvers and bulk operations.
- Can caller-controlled identifiers, claims, headers, role attributes or tenancy context bypass checks? Are default-deny and revocation/session expiry valid across failure and async paths?
- Are CSRF, CORS, redirect and cookie policies appropriate to browser-based authenticated actions? Separate authentication, authorization and UI-only gates.

## Secrets, sensitive data, and isolation
- Can tokens, credentials, private keys, personal data or internal details leak via source, config, logs, errors, tracing, telemetry, artifacts, caches or API responses?
- Are secret rotation and scope assumptions enforced? Are sensitive records isolated between tenants and environments, including backups and debug paths?
- Do not open or print secret values merely to prove they exist; cite the variable/config path or handling code.

## Cryptography and integrity
- Is a vetted primitive used correctly, with sound mode, nonce/IV, randomness, key origin/lifetime, verification-before-use and constant-time comparison where required?
- Are signatures, webhooks, package/artifact integrity and replay protection bound to the correct identity, context and expiration?

## Dependencies and supply chain
- Are changed direct/transitive dependencies, lockfile changes, build steps, install hooks, generated artifacts or CI permissions capable of executing code or changing trust boundaries?
- Cross-check exact versions, advisories and reachability when authorized data/tools exist. A package name or scanner label alone does not establish a reachable exploit.

## Filesystem, runtime, and network
- Can untrusted input control subprocess arguments, executable names, paths, filesystem permissions, symlinks, archive extraction, external requests or cloud resources?
- Examine sandbox, least privilege, tenancy, concurrency, race conditions, retries, idempotency, and unsafe defaults.

## Failure paths and business logic
- On malformed input, timeouts, partial writes, missing policy, stale caches or downstream outages, do controls fail open? Can retries, replay or sequencing violate authorization or financial/usage limits?
- Are security checks enforced at the authoritative side of the boundary, rather than only client-side or in a preflight path?

## AI/agent and tool boundaries (only if applicable)
- Can retrieved documents, repository files, issues, web pages, or tool outputs redirect tool use, reveal secrets, or cross authorization boundaries via prompt injection?
- Is tool authorization independent of model instructions, with least-privilege access and approval for destructive/external actions? Are model-generated shell, SQL, URLs or code treated as untrusted inputs?
