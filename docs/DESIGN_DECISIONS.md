# Design principles

The full contract is [ARCHITECTURE_SPEC.md](ARCHITECTURE_SPEC.md). These principles explain source, knowledge, work and transaction behavior.

1. Native exports are immutable files, registered once per original byte sequence and provider/environment. Shared exports support multiple permanent conversation IDs. Message UUIDs survive append-only expansion. Conflicting content remains in a distinct immutable export with an unresolved exception.
2. Explicit metadata discovery prevents arbitrary original JSON/YAML and attachments from being interpreted as repository records. Source paths are repository-relative, confined, and hashed. Each normalized message also stores a content checksum to detect accidental derived transcript changes.
3. UUIDv4 identities are independent of names, paths, providers, and times. Unicode NFKC, case folding, and whitespace normalization support lookup without approximate identity merging. Native-ID absence is explicit and ambiguous fingerprint matches require provenance review.
4. Markdown work records at schema version 3 combine structured operations and a substantial narrative. Outcomes are independent of lifecycle status. Hierarchy, dependencies, and succession use separate directed graphs; reciprocal parent/child links are valid.
5. CURRENT is reviewed interpretation. Associating a source records classified evidence and chronological evolution without automatically changing an established position. The command layer cannot settle contradictory meaning.
6. Agenda, registry, aliases, topic Markdown, and subject navigation are deterministic views. One runtime schema definition exports reviewable JSON schemas; validation detects drift. Templates direct callers to canonical generators to prevent competing record definitions.
7. IANA zones and explicit datetime offsets preserve DST semantics. Date-only obligations remain calendar dates. The agenda sorts date-only commitments by calendar date and instants by UTC; an explicit type tie-break avoids assigning imaginary midnight instants.
8. CLI mutations use cooperative advisory locks, changed-file overlays, incremental validation of affected records and relationships, and per-replacement precondition hashes before atomic per-file publication. A private Git-directory journal preserves a staging checkpoint if multi-file publication is interrupted. Git remote leases separately protect publication across independent clones.
9. Git receipts are created only after real fetch and ancestry verification. Source and derived commits precede the receipt. Historical receipts validate through ancestry after later commits. No commit claims its own SHA.
10. GitHub Actions use read-only permissions and sanitized summaries. Daily operational findings, weekly structural integrity and recent-run coverage, and monthly fidelity preparation have distinct scopes. Use the user-review procedure for source interpretation and verify external outcomes through their evidence.
11. Python 3.11+, PyYAML, jsonschema, zoneinfo, Git, Markdown and YAML keep the runtime portable. Supported native parsers and generic mappings are distinct from live account access; see PROVIDER_ADAPTERS.md.

12. Attachment completeness is a source-inventory reconciliation assertion, not a registration side effect. Canonical logical IDs exclude conflicting evidence versions. Expanded source scope always reopens review; unknown counts never imply zero.
13. Git resolves locks/journals per active checkout, including external linked-worktree metadata. This trusted metadata location is distinct from strictly contained repository-content paths.
14. Structural validation, user interpretation review and external access verification have separate scopes. Preserve explicit review state rather than promoting an unchecked assertion.


