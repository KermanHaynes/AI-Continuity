> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Reconciliation

Historical archival reconciliation is limited to source identity, chronology, snapshot observations, exact dialogue, message mappings and navigation. Intellectual reconciliation follows a separate user-guided review. Review stamps identify the exact transcript checksum, approved message scope, approval evidence, completion time, downstream references and deferred material. Reviewed does not mean every statement is true or adopted. Extensions retain prior review history and leave new material pending without moving the transcript.

---

The detailed operating requirements below apply to the stated operation.

## Procedure

Executable guidance: For every materially affected subject/work ID record changed, verified_unchanged, not_applicable or incomplete in an INDEX/PROCESSING/<transaction-id>.yaml checkpoint. Use schema processing.schema.json; validate before committing. Evidence review governs interpretations; no command synthesizes acceptance. `set-processing` validates complete assertions before publishing. Retain the original source chain, regenerate derived views, validate, and commit derived changes separately from originals. User-established durable context alone belongs in CONTEXT.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

# 3. Sources of Truth and Authority Hierarchy

There are four separate forms of authority.

**Original source authority:** Native provider exports and original attachments represent what was actually recorded.

**Interpretive authority:** KNOWLEDGE represents reviewed understanding derived from evidence. It must distinguish user-established positions from model suggestions.

**Operational authority:** WORK records represent established activities, statuses, commitments, dates, dependencies, external interactions, and outcomes.

**Historical transaction authority:** Git commits and durable transaction receipts represent changes actually preserved in the repository.

A derived record cannot overwrite, replace, or retrospectively rewrite original evidence.

A model-generated suggestion cannot become a user decision merely because it appears in a transcript.

A completed technical operation cannot be treated as an externally realized outcome.

An index or agenda cannot become a competing authority against its underlying record.

If two sources disagree, preserve both and identify the conflict. Do not silently resolve it.

Unknown information must remain unknown.

---

# 10. Global Context

`CONTEXT/` contains durable, broadly applicable preferences, working methods, writing style, and resources.

Do not populate these files with invented personal facts.

Only durable user-established information belongs here.

Do not promote a single situational preference into a global instruction without evidence.

`RESOURCES.md` distinguishes:

- A resource known to exist
- A resource connected to the present environment
- A resource accessible and verified
- A resource unavailable or requiring authorization

Never infer access to a provider transcript from access to GitHub.

---

# 12. Session Closeout Operating Contract

Closeout requires an explicit user instruction.

The operation sequence is:

## A. Preflight

Identify provider, environment, session identity, cutoff, native export accessibility, attachments, completeness, and current Git state.

If source capture is unavailable, do not claim complete archival.

## B. Preservation

Preserve actual source bytes.

Create or reuse permanent identities.

Generate validated normalized records.

Commit source preservation separately.

## C. Reconciliation

Identify every materially affected subject and work record.

For each affected record, classify the operation as:

- Changed
- Verified unchanged
- Not applicable
- Incomplete

Preserve historical reasoning, accepted decisions, revisions, outcomes, obligations, and unresolved issues.

Regenerate indexes and agenda.

Validate.

Commit derived changes separately.

## D. Concurrency

Compare the original starting SHA to the latest remote state.

If there are concurrent changes:

- Integrate unrelated changes.
- Reconcile compatible overlapping changes without losing either.
- Preserve competing evidence when meaning conflicts.
- Escalate unresolved authoritative contradictions for user judgment.

Never silently apply last-writer-wins.

## E. Remote verification

Push the authorized transaction.

Verify actual remote commit ancestry.

Confirm the preservation and derived commits are remotely reachable.

Record the observed branch, SHA, time, and verification mechanism.

## F. Receipt

Create a subsequent receipt/attestation record referencing the already-created commits.

Commit and verify that receipt separately.

Return actual full commit SHAs and GitHub links, validation results, affected IDs, and limitations.

Do not place a commit's own SHA inside its own contents.

A historical closeout remains valid after subsequent ordinary commits advance the repository.

Do not equate caller-supplied verification flags with actual remote verification.

---
