## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/130

**Issue title:** Docker doesn't set memory limits, causing all RAM to be used on low-memory machines

**Tier:** [ ] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The project's docker-compose.yml starts an LLM proxy container without any memory limit configured, so it can consume as much RAM as the host machine has available. On lower-end development machines (around 8GB of RAM), this causes the container to use up nearly all available memory, which leads the operating system to kill other running services (OOM kill) instead of the proxy handling the limit gracefully. The fix involves adding resource constraints (such as mem_limit or a deploy.resources.limits block, depending on the Compose version) to the LLM proxy service definition, sized to the project's minimum supported hardware. This is a Docker Compose configuration change, not an application code change, so success means the proxy still runs correctly under the new memory limit.

**Branch name:** fix/130-docker-memory-limits

**Setup confirmation:** [ ] App runs locally at localhost:5173

**Cohort ledger:** [ ] Issue added to cohort ledger
