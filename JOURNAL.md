## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/130

**Issue title:** Docker doesn't set memory limits, causing all RAM to be used on low-memory machines

**Tier:** [ ] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The project's docker-compose.yml starts an LLM proxy container without any memory limit configured, so it can consume as much RAM as the host machine has available. On lower-end development machines (around 8GB of RAM), this causes the container to use up nearly all available memory, which leads the operating system to kill other running services (OOM kill) instead of the proxy handling the limit gracefully. The fix involves adding resource constraints (such as mem_limit or a deploy.resources.limits block, depending on the Compose version) to the LLM proxy service definition, sized to the project's minimum supported hardware. This is a Docker Compose configuration change, not an application code change, so success means the proxy still runs correctly under the new memory limit.

**Branch name:** fix/130-docker-memory-limits

**Setup confirmation:** [ ] App runs locally at localhost:5173

**Cohort ledger:** [ ] Issue added to cohort ledger

## Reproduction notes (issue #130)

Investigated docker-compose.yml on current main (forked before any fix was merged).
Findings:
- No LLM proxy service exists in docker-compose.yml — only `db`, `redis`, and `vector-db` are defined.
- All three existing services already have `deploy.resources.limits.memory` set (db: 512M, redis: 256M, vector-db: 1G).
- `git log --oneline -- docker-compose.yml` shows only two commits (scaffold + initial working app) — no dedicated "add memory limits" fix, meaning limits were present from the start.
- Conclusion: the bug as described does not reproduce against current main. Commented on the issue to flag this and ask whether it's stale or whether a proxy service was expected to exist elsewhere.

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/GitNuckle/Pathreview/commit/fed26f1 

**Reproduction summary:**
Investigated docker-compose.yml and found no LLM proxy service currently defined, and all
existing services (db, redis, vector-db) already have memory limits set. The bug as
described in #130 does not reproduce against current main — flagged this on the issue.

**PLAN.md link:** https://github.com/GitNuckle/Pathreview/blob/fix/130-docker-memory-limits/PLAN.md

**Walkthrough video (recommended):** [not recorded]

**Blockers or open questions:**
Waiting to hear back on the issue about whether a proxy service was removed/never built,
or whether this issue is stale. My plan branches depending on that answer.
