## Solution plan

**Issue:** Docker doesn't set memory limits, causing all RAM to be used on low-memory machines (#130)
https://github.com/ascherj/pathreview/issues/130

### Understand
The issue describes an LLM proxy container in docker-compose.yml with no memory limit,
risking OOM kills on 8GB machines. On investigation, no LLM proxy service currently exists
in docker-compose.yml, and the three services that do exist (db, redis, vector-db) already
have deploy.resources.limits.memory configured. Expected behavior per the issue: every
service, including an LLM proxy, has a bounded memory limit. Actual behavior: no proxy
service is present to constrain, and existing services are already compliant.

### Map
- docker-compose.yml — the file the issue references directly
- scripts/issues_manifest.json — may contain metadata on issue status/history
- Any backend code referencing an LLM proxy (e.g. OPENROUTER_API_KEY usage) to confirm
  whether a proxy is meant to run as its own container or is handled differently now

### Plan
1. Confirm with the issue author / instructor whether this issue is stale or whether a
   proxy container was removed/refactored since the issue was filed.
2. If a proxy service should exist: add it to docker-compose.yml with an explicit
   deploy.resources.limits.memory block sized for 8GB minimum hardware (target ~1-1.5G,
   matching vector-db's precedent).
3. If no proxy container is required going forward: propose closing the issue with a
   comment explaining current state, or update docs to clarify LLM calls are proxied
   without a dedicated container.
4. Either way, verify all services in docker-compose.yml have consistent memory limits
   as a general hardening pass, since that's the actual spirit of the issue.
5. Re-run `docker compose up -d` and confirm all containers start and stay within limits
   (`docker stats`) on an 8GB-equivalent constraint.

### Inputs & outputs
Input: current docker-compose.yml, clarification from maintainer/instructor on whether
a proxy service is expected. Output: either a docker-compose.yml diff adding a properly
limited proxy service, or a documented resolution/close-out if the issue is stale.

### Risks & unknowns
- Unsure whether "LLM proxy" refers to a container that was planned but never built, or
  one that existed and was removed in a refactor — need maintainer input before writing
  code, to avoid solving a problem that doesn't exist.
- If I add a new service, I risk guessing wrong about what it should run (image, port,
  env vars) without more context from the codebase or issue author.
- Memory limits that are too low could cause the added service to crash/OOM itself;
  need to pick a reasonable value and test it under load.

### Edge cases
- Host machine at exactly 8GB — limits need enough headroom for db+redis+vector-db+proxy
  to coexist without exceeding total RAM.
- Proxy container restarting repeatedly due to memory limit being too strict (crash loop).
- Docker Desktop's own overhead on Windows/WSL2 reducing effectively available memory
  further than raw host RAM.
