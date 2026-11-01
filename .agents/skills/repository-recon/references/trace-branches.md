# Conditional tracing branches

Load only the sections relevant to the evidence encountered.

## Dynamic and plugin-driven execution

For dependency injection, registries, handlers, reflection, or plugin loading, inspect the registration site and selection condition, then verify a concrete binding from configuration, tests, or dispatch code. A definition alone does not establish a live runtime path. Where runtime registration cannot be determined statically, report candidate routes and the missing evidence.

## Generated artifacts

Distinguish canonical source inputs, generator invocation, generated outputs, and consumers. Prefer changing the canonical source in any later implementation workflow. If there are multiple generators or generated files disagree with source, mark authority unresolved rather than guessing.

## Frontend and API boundaries

Trace initiating UI event or endpoint, routing/middleware, domain operation, persistence/network effect, and response/error surface as applicable. Do not assume a request handler is the sole entry point; look for background jobs, CLI entry points, or scheduled tasks when task evidence points there.

## Data and asynchronous paths

Trace producer, schema/serialization, queue or storage, worker/consumer, error/retry behavior, and test fixtures. Separate eventual behavior inferred from conventions from code-backed transitions. Follow data lineage only far enough to determine the consequential change boundary.

## Monorepos and multiple implementations

Identify the active package using workspace manifests, build targets, imports, routing config or tests; check whether apparently duplicate code is active, deprecated, generated, or platform-specific. Do not infer ownership from directory names alone.
