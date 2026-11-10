> Operation authority: [OPERATING_RULES.md](../OPERATING_RULES.md) governs the selected task. Historical reconstruction reads every scoped conversation exhaustively and preserves the full artifact lineage; ordinary ongoing sessions use progressive retrieval. Faithful source capture, approval of intellectual changes and actual Git verification remain required.

# Session close

Integrated closeout requires deliberate user instruction. First examine the complete exchange and relevant records, propose retained developments, ideas, decisions, corrections, rejected alternatives, experiments, relationships, work, dates and unresolved questions. Distinguish evidence and interpretation; an assistant passage need not have contemporaneous acknowledgment to be worth reviewing. Obtain explicit approval of the concrete intellectual changes. Then preserve accessible native evidence and faithful transcript, disclose capture limitations, apply only approved downstream changes, preserve lineage, rebuild affected views and validate. Check concurrency; commit evidence and interpretation separately; push and fetch to verify ancestry; commit a durable receipt and return confirmation. No automatic closeout or knowledge processing is activated. Archive-only publication must not invent a derived knowledge commit or certify integrated completion.

---

The detailed operating requirements below apply to the stated operation.

## Procedure

Executable guidance: Run `validate`, then follow the separate preservation/reconciliation/receipt sequence below. Keep the starting SHA. Commit preservation, then derived reconciliation. Use `memory.transactions.concurrency` after fetching to inspect overlapping canonical paths; merge unrelated changes with ordinary Git merge, review compatible overlaps, and stop affected semantic conflicts for user judgment. Push normally (or connector update_ref with expected_sha); never force-overwrite a changed branch. Record an explicit processing checkpoint with the already-created preservation and derived SHAs. The `closeout-record` command fetches the named remote branch and verifies reachability before writing the receipt. Commit the receipt separately and push, then fetch and verify its SHA. Report native-capture limitations truthfully. A session ending does not authorize archival closeout.

Commands emit JSON and exit 0 on success, 1 on blocking validation findings, or 2 on invalid input/operation failure. Full CLI arguments: [SETUP](../SETUP.md).

The following record and operation requirements apply.

# 12. Session Closeout Operating Contract

Closeout requires an explicit user instruction.

The operation sequence is:

## A. Preflight

Obtain the faithful transcript through the opening capture plan. Request any user-supplied export before claiming completed preservation; never substitute a summary.

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
