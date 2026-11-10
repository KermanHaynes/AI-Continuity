# Multiple reconstruction agents

The recommended default is **one agent per complete topic or project**. Each agent owns its topic’s scope, exhaustive reading, complete evolution record, draft, user review, approved final and current knowledge.

All agents may read the same immutable SOT sources. Each must independently read every available conversation within its defined historical scope; another topic agent’s summary or search results do not replace that coverage. Keep reading checkpoints, notes, artifacts and lineage separate by topic/run identity.

Do not normally split a single topic among agents by date, provider, batch or subsection. That fragmentation makes it easier to lose relationships, reasons for changes or a late reconsideration of an earlier branch. A user may explicitly organize exceptional work differently, but the topic owner still has responsibility for complete scope coverage and integrated evolution.

Use separate agent working environments or temporary branches where actual writes may overlap. The agent handles checkout/worktree setup available in its environment; the user should not need to manage those mechanics. Preserve the existing shared immutable source identities and avoid duplicating SOT merely because multiple agents read it.

Before publishing, fetch and inspect concurrent changes. Merge independent work normally, review compatible overlaps and present genuine semantic conflicts for user judgment. Do not silently apply last-writer-wins to shared registries, CURRENT or operational work. One agent’s completion does not complete another topic’s coverage.

The [artifact conventions](RECONSTRUCTION_ARTIFACTS.md) and [Git operating rules](GIT_OPERATIONS.md) provide the required persistence and recovery behavior without an additional multi-agent architecture.
